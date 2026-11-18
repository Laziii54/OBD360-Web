import { Service, computed, signal } from '@angular/core';

// Minimal Web Bluetooth typings: TypeScript's DOM library does not include this API.
interface GattCharacteristic extends EventTarget {
  uuid: string;
  value?: DataView;
  properties: {
    notify: boolean;
    indicate: boolean;
    write: boolean;
    writeWithoutResponse: boolean;
  };
  startNotifications(): Promise<GattCharacteristic>;
  writeValueWithResponse(value: Uint8Array): Promise<void>;
  writeValueWithoutResponse(value: Uint8Array): Promise<void>;
}

interface GattService {
  uuid: string;
  getCharacteristics(): Promise<GattCharacteristic[]>;
}

interface GattServer {
  connected: boolean;
  connect(): Promise<GattServer>;
  disconnect(): void;
  getPrimaryServices(): Promise<GattService[]>;
}

interface BluetoothAdapterDevice extends EventTarget {
  name?: string;
  gatt?: GattServer;
}

interface WebBluetooth {
  requestDevice(options: {
    filters: { namePrefix: string }[];
    optionalServices: (number | string)[];
  }): Promise<BluetoothAdapterDevice>;
}

export type AdapterStatus = 'disconnected' | 'connecting' | 'initializing' | 'connected';

interface PendingCommand {
  resolve: (response: string) => void;
  reject: (error: Error) => void;
  timer: ReturnType<typeof setTimeout>;
}

const ADAPTER_NAME_PREFIXES = ['KONNWEI', 'OBD', 'ELM', 'MAXOBD', 'KW', 'Vgate', 'vLinker', 'V-LINK'];

// Web Bluetooth can only open services listed here, so these are the ones used by BLE ELM327 adapters.
const ADAPTER_SERVICES: (number | string)[] = [
  0xfff0,
  0xffe0,
  0x18f0,
  'e7810a71-73ae-499d-8c15-faa9aef0c3f2',
  '6e400001-b5a3-f393-e0a9-e50e24dcca9e',
];

const BLE_CHUNK_SIZE = 20;
const DEFAULT_TIMEOUT_MS = 4000;
const RESET_TIMEOUT_MS = 8000;
const VEHICLE_TIMEOUT_MS = 15000;
const MAX_LOG_LINES = 100;

@Service()
export class ObdBluetooth {
  private device: BluetoothAdapterDevice | null = null;
  private writer: GattCharacteristic | null = null;
  private notifier: GattCharacteristic | null = null;
  private pending: PendingCommand | null = null;
  private buffer = '';
  private queue: Promise<unknown> = Promise.resolve();

  private readonly encoder = new TextEncoder();
  private readonly decoder = new TextDecoder();
  private readonly onValue = (event: Event): void => this.handleValue(event);
  private readonly onDisconnected = (): void => this.handleDisconnected();

  readonly isSupported = 'bluetooth' in navigator;

  readonly status = signal<AdapterStatus>('disconnected');
  readonly adapterName = signal<string | null>(null);
  readonly elmVersion = signal<string | null>(null);
  readonly protocol = signal<string | null>(null);
  readonly voltage = signal<string | null>(null);
  readonly vehicleResponding = signal(false);
  readonly errorMessage = signal<string | null>(null);
  readonly log = signal<string[]>([]);

  readonly isConnected = computed(() => this.status() === 'connected');
  readonly isCan = computed(() => this.protocol()?.toUpperCase().includes('CAN') ?? true);
  readonly isBusy = computed(() => ['connecting', 'initializing'].includes(this.status()));

  // Must be called from a click: browsers only open the device chooser after a user gesture.
  async connect(): Promise<void> {
    const bluetooth = (navigator as unknown as { bluetooth?: WebBluetooth }).bluetooth;
    if (!bluetooth) {
      this.errorMessage.set('This browser does not support Web Bluetooth. Use Chrome or Edge.');
      return;
    }

    this.errorMessage.set(null);
    this.log.set([]);
    this.status.set('connecting');

    try {
      const device = await bluetooth.requestDevice({
        filters: ADAPTER_NAME_PREFIXES.map((namePrefix) => ({ namePrefix })),
        optionalServices: ADAPTER_SERVICES,
      });

      this.device = device;
      this.adapterName.set(device.name ?? 'Unknown adapter');
      device.addEventListener('gattserverdisconnected', this.onDisconnected);

      if (!device.gatt) {
        throw new Error('This device does not offer a Bluetooth LE connection.');
      }

      const server = await device.gatt.connect();
      await this.findCharacteristics(server);

      this.status.set('initializing');
      await this.initializeAdapter();
      this.status.set('connected');
    } catch (error) {
      const cancelled = error instanceof DOMException && error.name === 'NotFoundError';
      if (!cancelled) {
        this.errorMessage.set(error instanceof Error ? error.message : 'The connection failed.');
      }
      this.disconnect();
      this.handleDisconnected();
    }
  }

  disconnect(): void {
    if (this.device?.gatt?.connected) {
      this.device.gatt.disconnect();
    }
  }

  // Commands run one at a time, because an ELM327 answers only one command at once.
  send(command: string, timeoutMs = DEFAULT_TIMEOUT_MS): Promise<string> {
    const run = (): Promise<string> => this.transmit(command, timeoutMs);
    const result = this.queue.then(run, run);
    this.queue = result.catch(() => undefined);
    return result;
  }

  private async findCharacteristics(server: GattServer): Promise<void> {
    let services: GattService[];
    try {
      services = await server.getPrimaryServices();
    } catch {
      throw new Error('No supported adapter service was found on this device.');
    }

    for (const service of services) {
      const characteristics = await service.getCharacteristics();
      this.addLog(`Service ${service.uuid}`);

      for (const item of characteristics) {
        const flags = Object.entries({
          notify: item.properties.notify,
          indicate: item.properties.indicate,
          write: item.properties.write,
          writeNoResponse: item.properties.writeWithoutResponse,
        })
          .filter(([, enabled]) => enabled)
          .map(([name]) => name)
          .join(', ');
        this.addLog(`  ${item.uuid} (${flags})`);
      }

      const notifier = characteristics.find((c) => c.properties.notify || c.properties.indicate);
      const writer = characteristics.find((c) => c.properties.write || c.properties.writeWithoutResponse);

      if (notifier && writer) {
        await notifier.startNotifications();
        notifier.addEventListener('characteristicvaluechanged', this.onValue);
        this.notifier = notifier;
        this.writer = writer;
        return;
      }
    }

    throw new Error('This device has no readable and writable adapter channel.');
  }

  private async initializeAdapter(): Promise<void> {
    const reset = await this.send('ATZ', RESET_TIMEOUT_MS);
    if (!reset.toUpperCase().includes('ELM')) {
      throw new Error('This device did not answer as an ELM327 adapter.');
    }

    this.elmVersion.set(reset.match(/ELM\S*\s*v?[\d.]+/i)?.[0] ?? reset);

    for (const command of ['ATE0', 'ATL0', 'ATS0', 'ATH0', 'ATSP0']) {
      await this.send(command);
    }

    this.voltage.set(await this.send('ATRV'));

    // 0100 asks the ECU for its supported PIDs, which also selects the vehicle protocol.
    try {
      const vehicle = await this.send('0100', VEHICLE_TIMEOUT_MS);
      this.vehicleResponding.set(vehicle.replace(/\s/g, '').toUpperCase().includes('4100'));
      this.protocol.set(await this.send('ATDP'));
    } catch {
      this.vehicleResponding.set(false);
    }
  }

  private async transmit(command: string, timeoutMs: number): Promise<string> {
    const writer = this.writer;
    if (!writer) {
      throw new Error('The adapter is not connected.');
    }

    this.buffer = '';
    this.addLog(`> ${command}`);

    const response = new Promise<string>((resolve, reject) => {
      const timer = setTimeout(() => {
        this.pending = null;
        reject(new Error(`The adapter did not answer "${command}" in time.`));
      }, timeoutMs);
      this.pending = { resolve, reject, timer };
    });

    const bytes = this.encoder.encode(`${command}\r`);
    for (let offset = 0; offset < bytes.length; offset += BLE_CHUNK_SIZE) {
      const chunk = bytes.slice(offset, offset + BLE_CHUNK_SIZE);
      if (writer.properties.writeWithoutResponse) {
        await writer.writeValueWithoutResponse(chunk);
      } else {
        await writer.writeValueWithResponse(chunk);
      }
    }

    return response;
  }

  // An ELM327 response can span many notifications and always ends with the ">" prompt.
  private handleValue(event: Event): void {
    const value = (event.target as GattCharacteristic).value;
    if (!value) {
      return;
    }

    this.buffer += this.decoder.decode(value);
    const end = this.buffer.indexOf('>');
    if (end === -1 || !this.pending) {
      return;
    }

    const response = this.buffer.slice(0, end).replace(/\0/g, '').replace(/[\r\n]+/g, '\n').trim();
    this.buffer = '';
    this.addLog(`< ${response.replace(/\n/g, ' ')}`);

    const { resolve, timer } = this.pending;
    this.pending = null;
    clearTimeout(timer);
    resolve(response);
  }

  private handleDisconnected(): void {
    this.notifier?.removeEventListener('characteristicvaluechanged', this.onValue);
    this.device?.removeEventListener('gattserverdisconnected', this.onDisconnected);

    if (this.pending) {
      clearTimeout(this.pending.timer);
      this.pending.reject(new Error('The adapter disconnected.'));
      this.pending = null;
    }

    this.device = null;
    this.writer = null;
    this.notifier = null;
    this.buffer = '';
    this.status.set('disconnected');
    this.adapterName.set(null);
    this.elmVersion.set(null);
    this.protocol.set(null);
    this.voltage.set(null);
    this.vehicleResponding.set(false);
  }

  private addLog(line: string): void {
    this.log.update((lines) => [...lines, line].slice(-MAX_LOG_LINES));
  }
}
