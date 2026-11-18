import { Component, computed, inject, signal } from '@angular/core';
import { parseEcuAddresses } from '../../core/services/obd-decoder';
import { ObdBluetooth } from '../../core/services/obd-bluetooth.service';

interface EcuModule {
  address: string;
  name: string;
  description: string;
}

const KNOWN_MODULES: Record<string, Omit<EcuModule, 'address'>> = {
  '7E8': { name: 'Engine Control Module', description: 'Responds on the standard engine address.' },
  '10': { name: 'Engine Control Module', description: 'Responds on the standard engine address.' },
  '7E9': { name: 'Transmission Control Module', description: 'Responds on the standard transmission address.' },
  '18': { name: 'Transmission Control Module', description: 'Responds on the standard transmission address.' },
};

@Component({
  imports: [],
  selector: 'app-ecu-modules',
  styleUrl: './ecu-modules.scss',
  templateUrl: './ecu-modules.html',
})
export class EcuModules {
  readonly adapter = inject(ObdBluetooth);

  readonly scanning = signal(false);
  readonly scanned = signal(false);
  readonly modules = signal<EcuModule[]>([]);
  readonly errorMessage = signal<string | null>(null);

  readonly summaryLabel = computed(() => (this.scanned() ? 'SCAN COMPLETE' : 'NOT SCANNED'));

  // Header output is only needed here, because it changes the format of every other response.
  async scan(): Promise<void> {
    this.scanning.set(true);
    this.errorMessage.set(null);

    try {
      await this.adapter.send('ATH1');
      const addresses = parseEcuAddresses(await this.adapter.send('0100', 10000));

      this.modules.set(
        addresses.map((address) => ({
          address,
          ...(KNOWN_MODULES[address] ?? {
            name: 'OBD-II Module',
            description: 'Responds to standard OBD-II requests.',
          }),
        }))
      );
      this.scanned.set(true);

      if (!addresses.length) {
        this.errorMessage.set('No CAN modules answered. Older protocols do not report module addresses.');
      }
    } catch (error) {
      this.errorMessage.set(error instanceof Error ? error.message : 'The module scan failed.');
    } finally {
      await this.adapter.send('ATH0').catch(() => undefined);
      this.scanning.set(false);
    }
  }
}
