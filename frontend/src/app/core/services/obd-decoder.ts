export interface PidDefinition {
  id: string;
  pid: string;
  name: string;
  category: string;
  unit: string;
  icon: string;
  iconClass: string;
  digits: number;
  decode: (bytes: number[]) => number;
}

export type DtcMode = '03' | '07' | '0A';
export type MonitorState = 'ready' | 'incomplete' | 'unsupported';

export interface ReadinessMonitor {
  name: string;
  state: MonitorState;
}

export interface VehicleStatus {
  milOn: boolean;
  storedCount: number;
  monitors: ReadinessMonitor[];
}

const percent = ([a]: number[]): number => (a * 100) / 255;
const temperature = ([a]: number[]): number => a - 40;

export const LIVE_PIDS: PidDefinition[] = [
  { id: 'rpm', pid: '010C', name: 'Engine RPM', category: 'ENGINE', unit: 'rpm', icon: '◉', iconClass: 'rpm-icon', digits: 0, decode: ([a, b]) => (a * 256 + b) / 4 },
  { id: 'speed', pid: '010D', name: 'Vehicle Speed', category: 'VEHICLE', unit: 'km/h', icon: '➤', iconClass: 'speed-icon', digits: 0, decode: ([a]) => a },
  { id: 'coolant', pid: '0105', name: 'Coolant Temperature', category: 'ENGINE', unit: '°C', icon: '♨', iconClass: 'temp-icon', digits: 0, decode: temperature },
  { id: 'load', pid: '0104', name: 'Engine Load', category: 'ENGINE', unit: '%', icon: '▥', iconClass: 'load-icon', digits: 1, decode: percent },
  { id: 'throttle', pid: '0111', name: 'Throttle Position', category: 'ENGINE', unit: '%', icon: '◈', iconClass: 'throttle-icon', digits: 1, decode: percent },
  { id: 'voltage', pid: '0142', name: 'Control Module Voltage', category: 'ELECTRICAL', unit: 'V', icon: 'ϟ', iconClass: 'voltage-icon', digits: 2, decode: ([a, b]) => (a * 256 + b) / 1000 },
  { id: 'intake', pid: '010F', name: 'Intake Air Temperature', category: 'ENGINE', unit: '°C', icon: '❄', iconClass: 'intake-icon', digits: 0, decode: temperature },
  { id: 'fuelTrim', pid: '0106', name: 'Short Term Fuel Trim', category: 'FUEL SYSTEM', unit: '%', icon: '◉', iconClass: 'fuel-icon', digits: 1, decode: ([a]) => ((a - 128) * 100) / 128 },
];

const compact = (raw: string): string[] =>
  raw
    .toUpperCase()
    .split('\n')
    .map((line) => line.replace(/\s/g, ''))
    .filter(Boolean);

const toBytes = (hex: string): number[] => (hex.match(/../g) ?? []).map((pair) => parseInt(pair, 16));

/** Returns the data bytes of a mode 01 response, or null when the vehicle gave no usable answer. */
export function parsePidBytes(raw: string, pid: string): number[] | null {
  const prefix = `41${pid.slice(2)}`;
  const line = compact(raw).find((item) => item.startsWith(prefix) && /^[0-9A-F]+$/.test(item));
  return line ? toBytes(line.slice(prefix.length)) : null;
}

export function decodePid(raw: string, definition: PidDefinition): number | null {
  const bytes = parsePidBytes(raw, definition.pid);
  return bytes?.length ? definition.decode(bytes) : null;
}

export function decodeDtc(hex: string): string {
  const first = parseInt(hex[0], 16);
  return `${'PCBU'[first >> 2]}${first & 3}${hex.slice(1)}`;
}

/** Decodes mode 03, 07 and 0A responses. CAN responses carry a count byte and may span several frames. */
export function parseDtcResponse(raw: string, mode: DtcMode, isCan: boolean): string[] {
  const marker = (0x40 + parseInt(mode, 16)).toString(16).toUpperCase();
  const lines = compact(raw).filter((line) => /^[0-9A-F:]+$/.test(line));
  const frames = lines.filter((line) => /^[0-9A-F]:/.test(line));

  const payloads = frames.length
    ? [frames.map((frame) => frame.slice(2)).join('')]
    : lines.filter((line) => line.startsWith(marker));

  const codes = new Set<string>();

  for (const payload of payloads) {
    if (!payload.startsWith(marker)) {
      continue;
    }

    let body = payload.slice(2);
    if (isCan) {
      const count = parseInt(body.slice(0, 2), 16);
      body = body.slice(2, 2 + count * 4);
    }

    for (let index = 0; index + 4 <= body.length; index += 4) {
      const chunk = body.slice(index, index + 4);
      if (chunk !== '0000') {
        codes.add(decodeDtc(chunk));
      }
    }
  }

  return [...codes];
}

const monitorState = (supportByte: number, incompleteByte: number, bit: number): MonitorState => {
  if (!(supportByte & (1 << bit))) {
    return 'unsupported';
  }
  return incompleteByte & (1 << bit) ? 'incomplete' : 'ready';
};

/** Decodes PID 0101. Catalyst, oxygen, EVAP and EGR bits only apply to spark ignition engines. */
export function parseVehicleStatus(raw: string): VehicleStatus | null {
  const bytes = parsePidBytes(raw, '0101');
  if (!bytes || bytes.length < 4) {
    return null;
  }

  const [a, b, c, d] = bytes;
  const isSpark = !(b & 0x08);
  const sparkMonitor = (bit: number): MonitorState => (isSpark ? monitorState(c, d, bit) : 'unsupported');

  return {
    milOn: Boolean(a & 0x80),
    storedCount: a & 0x7f,
    monitors: [
      { name: 'Catalyst Monitor', state: sparkMonitor(0) },
      { name: 'Oxygen Sensor', state: sparkMonitor(5) },
      { name: 'EVAP System', state: sparkMonitor(2) },
      { name: 'EGR System', state: sparkMonitor(7) },
      { name: 'Misfire Monitor', state: monitorState(b, b >> 4, 0) },
      { name: 'Fuel System Monitor', state: monitorState(b, b >> 4, 1) },
    ],
  };
}

export type UnitSystem = 'metric' | 'imperial';

const MANIFOLD_PRESSURE_PID: PidDefinition = {
  id: 'map',
  pid: '010B',
  name: 'Intake Manifold Pressure',
  category: 'ENGINE',
  unit: 'kPa',
  icon: '⌖',
  iconClass: 'map-icon',
  digits: 0,
  decode: ([a]) => a,
};

export const FREEZE_PIDS: PidDefinition[] = [
  ...LIVE_PIDS.filter((definition) => definition.id !== 'voltage'),
  MANIFOLD_PRESSURE_PID,
];

/** Converts a metric reading for display. */
export function convertReading(value: number, unit: string, system: UnitSystem): { value: number; unit: string } {
  if (system === 'imperial' && unit === 'km/h') {
    return { value: value * 0.621371, unit: 'mph' };
  }
  if (system === 'imperial' && unit === '°C') {
    return { value: (value * 9) / 5 + 32, unit: '°F' };
  }
  if (system === 'imperial' && unit === 'kPa') {
    return { value: value * 0.145038, unit: 'psi' };
  }
  return { value, unit };
}

/** Decodes a mode 02 response for frame 00, which echoes the PID and the frame number. */
export function decodeFreezeValue(raw: string, definition: PidDefinition): number | null {
  const prefix = `42${definition.pid.slice(2)}00`;
  const line = compact(raw).find((item) => item.startsWith(prefix) && /^[0-9A-F]+$/.test(item));
  const bytes = line ? toBytes(line.slice(prefix.length)) : [];
  return bytes.length ? definition.decode(bytes) : null;
}

/** Returns the DTC that stored freeze frame 00, or null when no frame exists. */
export function parseFreezeDtc(raw: string): string | null {
  const line = compact(raw).find((item) => item.startsWith('420200') && /^[0-9A-F]+$/.test(item));
  const hex = line?.slice(6, 10);
  return hex && hex.length === 4 && hex !== '0000' ? decodeDtc(hex) : null;
}

/** Reads the VIN from a multi-frame CAN response to 0902. */
export function parseVin(raw: string): string | null {
  const frames = compact(raw).filter((line) => /^[0-9A-F]:/.test(line));
  const payload = frames.map((frame) => frame.slice(2)).join('');
  const start = payload.indexOf('490201');
  if (start === -1) {
    return null;
  }

  const vin = String.fromCharCode(...toBytes(payload.slice(start + 6, start + 40)));
  return /^[A-HJ-NPR-Z0-9]{17}$/.test(vin) ? vin : null;
}

/** Lists responding CAN modules from a response received with headers enabled. */
export function parseEcuAddresses(raw: string): string[] {
  const addresses = new Set<string>();

  for (const line of compact(raw)) {
    const standard = line.match(/^(7E[8-9A-F])/);
    const extended = line.match(/^18DAF1([0-9A-F]{2})/);
    if (standard) {
      addresses.add(standard[1]);
    } else if (extended) {
      addresses.add(extended[1]);
    }
  }

  return [...addresses].sort();
}
