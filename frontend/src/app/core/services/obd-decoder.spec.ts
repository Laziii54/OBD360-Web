import { describe, expect, it } from 'vitest';
import {
  LIVE_PIDS,
  convertReading,
  decodeDtc,
  decodeFreezeValue,
  decodePid,
  parseDtcResponse,
  parseEcuAddresses,
  parseFreezeDtc,
  parsePidBytes,
  parseVehicleStatus,
  parseVin,
} from './obd-decoder';

const definition = (pid: string) => {
  const found = LIVE_PIDS.find((item) => item.pid === pid);
  if (!found) {
    throw new Error(`Unknown PID ${pid}`);
  }
  return found;
};

describe('obd-decoder', () => {
  describe('parsePidBytes', () => {
    it('returns the data bytes of a mode 01 response', () => {
      expect(parsePidBytes('41 0C 1A F8', '010C')).toEqual([0x1a, 0xf8]);
    });

    it('ignores other PIDs in the same answer', () => {
      expect(parsePidBytes('41 0D 50\n41 0C 1A F8', '010C')).toEqual([0x1a, 0xf8]);
    });

    it('returns null for NO DATA', () => {
      expect(parsePidBytes('NO DATA', '010C')).toBeNull();
    });
  });

  describe('decodePid', () => {
    it('decodes engine RPM (010C) as (A*256+B)/4', () => {
      expect(decodePid('41 0C 1A F8', definition('010C'))).toBe(1726);
    });

    it('decodes vehicle speed (010D)', () => {
      expect(decodePid('41 0D 32', definition('010D'))).toBe(50);
    });

    it('decodes coolant temperature (0105) with the -40 offset', () => {
      expect(decodePid('41 05 7B', definition('0105'))).toBe(83);
    });

    it('decodes battery voltage (0142) in volts', () => {
      expect(decodePid('41 42 30 39', definition('0142'))).toBeCloseTo(12.345, 3);
    });

    it('returns null when the vehicle did not answer', () => {
      expect(decodePid('NO DATA', definition('010C'))).toBeNull();
    });
  });

  describe('decodeDtc', () => {
    it('decodes powertrain codes', () => {
      expect(decodeDtc('0300')).toBe('P0300');
      expect(decodeDtc('0171')).toBe('P0171');
    });

    it('decodes chassis, body and network codes from the first nibble', () => {
      expect(decodeDtc('4300')).toBe('C0300');
      expect(decodeDtc('8300')).toBe('B0300');
      expect(decodeDtc('C100')).toBe('U0100');
    });
  });

  describe('parseDtcResponse', () => {
    it('reads CAN responses with a count byte', () => {
      expect(parseDtcResponse('43 02 01 71 03 00', '03', true)).toEqual(['P0171', 'P0300']);
    });

    it('reads non-CAN responses without a count byte', () => {
      expect(parseDtcResponse('43 01 71 03 00', '03', false)).toEqual(['P0171', 'P0300']);
    });

    it('skips empty 0000 slots', () => {
      expect(parseDtcResponse('43 01 71 00 00', '03', false)).toEqual(['P0171']);
    });

    it('joins multi-frame answers', () => {
      expect(parseDtcResponse('0:43020171\n1:0300', '03', true)).toEqual(['P0171', 'P0300']);
    });

    it('returns nothing for a NO DATA answer', () => {
      expect(parseDtcResponse('NO DATA', '03', true)).toEqual([]);
    });
  });

  describe('parseVehicleStatus', () => {
    it('reads the MIL flag and the stored code count', () => {
      const status = parseVehicleStatus('41 01 81 07 65 04');
      expect(status).not.toBeNull();
      expect(status?.milOn).toBe(true);
      expect(status?.storedCount).toBe(1);
    });

    it('maps readiness monitors from the support and incomplete bytes', () => {
      const status = parseVehicleStatus('41 01 81 07 65 04');
      expect(status?.monitors.map((monitor) => monitor.state)).toEqual([
        'ready',
        'ready',
        'incomplete',
        'unsupported',
        'ready',
        'ready',
      ]);
    });

    it('returns null when the answer is too short', () => {
      expect(parseVehicleStatus('41 01 81')).toBeNull();
    });
  });

  describe('freeze frame', () => {
    it('decodes a mode 02 value for frame 00', () => {
      expect(decodeFreezeValue('42 0C 00 1A F8', definition('010C'))).toBe(1726);
    });

    it('reads the DTC that caused the freeze frame', () => {
      expect(parseFreezeDtc('42 02 00 03 00')).toBe('P0300');
    });

    it('returns null when the frame is empty', () => {
      expect(parseFreezeDtc('42 02 00 00 00')).toBeNull();
    });
  });

  describe('parseVin', () => {
    it('joins multi-frame CAN answers and returns the VIN', () => {
      const raw = [
        '0:49020131',
        '1:4847424834',
        '2:314A584D4E',
        '3:3130393138',
        '4:3600000000',
      ].join('\n');

      expect(parseVin(raw)).toBe('1HGBH41JXMN109186');
    });

    it('returns null for an invalid VIN', () => {
      expect(parseVin('0:49020131\n1:00')).toBeNull();
    });
  });

  describe('parseEcuAddresses', () => {
    it('collects standard and extended CAN module addresses', () => {
      const raw = [
        '7E8 06 41 00 BE 3F A8 13',
        '7E9 06 41 00 98 18 00 11',
        '18DAF110 06 41 00 BE 3F A8 13',
      ].join('\n');

      expect(parseEcuAddresses(raw)).toEqual(['10', '7E8', '7E9']);
    });
  });

  describe('convertReading', () => {
    it('converts km/h to mph', () => {
      const result = convertReading(100, 'km/h', 'imperial');
      expect(result.unit).toBe('mph');
      expect(result.value).toBeCloseTo(62.1371, 4);
    });

    it('converts Celsius to Fahrenheit', () => {
      expect(convertReading(100, '°C', 'imperial')).toEqual({ value: 212, unit: '°F' });
    });

    it('converts kPa to psi', () => {
      const result = convertReading(100, 'kPa', 'imperial');
      expect(result.unit).toBe('psi');
      expect(result.value).toBeCloseTo(14.5038, 4);
    });

    it('keeps metric values unchanged', () => {
      expect(convertReading(100, 'km/h', 'metric')).toEqual({ value: 100, unit: 'km/h' });
    });
  });
});
