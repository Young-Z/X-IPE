import { describe, expect, it, vi } from 'vitest';
import { UpdateOptionsCommand } from '../../../../src/editor/commands/UpdateOptions';
import { ZoomWheel } from '../../../../src/editor/interactions/zoom-wheel';

const createSVG = (width: number, height: number) => {
  const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
  (svg as any).getBBox = () => ({ x: 0, y: 0, width, height });
  return svg;
};

describe('ZoomWheel interaction', () => {
  describe('zoom in (deltaY > 0)', () => {
    it('zooms in from zero padding using initial value', () => {
      const svg = createSVG(100, 50);
      const commander = { execute: vi.fn() } as any;
      const interaction = { isActive: vi.fn(() => true) } as any;
      const state = {
        getOptions: vi.fn(() => ({ padding: 0 }) as any),
      } as any;

      const instance = new ZoomWheel();
      instance.init({
        emitter: {} as any,
        editor: { getDocument: () => svg } as any,
        commander,
        interaction,
        state,
      });

      const event = new WheelEvent('wheel', { deltaY: 120, ctrlKey: true });
      const preventDefaultSpy = vi.spyOn(event, 'preventDefault');
      document.dispatchEvent(event);

      expect(preventDefaultSpy).toHaveBeenCalled();
      expect(commander.execute).toHaveBeenCalledTimes(1);
      const command = commander.execute.mock.calls[0][0] as UpdateOptionsCommand;
      expect(command).toBeInstanceOf(UpdateOptionsCommand);
      // When padding is 0, zoom in uses INITIAL_PADDING_WHEN_ZERO (10) * ZOOM_IN_FACTOR (1.1) = 11
      expect(command.serialize().options).toEqual({
        padding: [11, 11, 11, 11],
      });

      instance.destroy();
    });

    it('zooms in from non-zero padding', () => {
      const svg = createSVG(100, 50);
      const commander = { execute: vi.fn() } as any;
      const interaction = { isActive: vi.fn(() => true) } as any;
      const state = {
        getOptions: vi.fn(() => ({ padding: 20 }) as any),
      } as any;

      const instance = new ZoomWheel();
      instance.init({
        emitter: {} as any,
        editor: { getDocument: () => svg } as any,
        commander,
        interaction,
        state,
      });

      const event = new WheelEvent('wheel', { deltaY: 120, ctrlKey: true });
      document.dispatchEvent(event);

      expect(commander.execute).toHaveBeenCalledTimes(1);
      const command = commander.execute.mock.calls[0][0] as UpdateOptionsCommand;
      // 20 * 1.1 = 22
      expect(command.serialize().options).toEqual({
        padding: [22, 22, 22, 22],
      });

      instance.destroy();
    });

    it('zooms in from array padding', () => {
      const svg = createSVG(100, 50);
      const commander = { execute: vi.fn() } as any;
      const interaction = { isActive: vi.fn(() => true) } as any;
      const state = {
        getOptions: vi.fn(() => ({ padding: [10, 20, 30, 40] }) as any),
      } as any;

      const instance = new ZoomWheel();
      instance.init({
        emitter: {} as any,
        editor: { getDocument: () => svg } as any,
        commander,
        interaction,
        state,
      });

      const event = new WheelEvent('wheel', { deltaY: 120, ctrlKey: true });
      document.dispatchEvent(event);

      expect(commander.execute).toHaveBeenCalledTimes(1);
      const command = commander.execute.mock.calls[0][0] as UpdateOptionsCommand;
      // [10, 20, 30, 40] * 1.1 = [11, 22, 33, 44]
      expect(command.serialize().options).toEqual({
        padding: [11, 22, 33, 44],
      });

      instance.destroy();
    });
  });

  describe('zoom out (deltaY < 0)', () => {
    it('zooms out from zero padding using negative initial value', () => {
      const svg = createSVG(100, 50);
      const commander = { execute: vi.fn() } as any;
      const interaction = { isActive: vi.fn(() => true) } as any;
      const state = {
        getOptions: vi.fn(() => ({ padding: 0 }) as any),
      } as any;

      const instance = new ZoomWheel();
      instance.init({
        emitter: {} as any,
        editor: { getDocument: () => svg } as any,
        commander,
        interaction,
        state,
      });

      const event = new WheelEvent('wheel', { deltaY: -120, ctrlKey: true });
      const preventDefaultSpy = vi.spyOn(event, 'preventDefault');
      document.dispatchEvent(event);

      expect(preventDefaultSpy).toHaveBeenCalled();
      expect(commander.execute).toHaveBeenCalledTimes(1);
      const command = commander.execute.mock.calls[0][0] as UpdateOptionsCommand;
      // When padding is 0, zoom out uses -INITIAL_PADDING_WHEN_ZERO (-10) * ZOOM_OUT_FACTOR (0.9) = -9
      expect(command.serialize().options).toEqual({
        padding: [-9, -9, -9, -9],
      });

      instance.destroy();
    });

    it('zooms out from non-zero padding', () => {
      const svg = createSVG(100, 50);
      const commander = { execute: vi.fn() } as any;
      const interaction = { isActive: vi.fn(() => true) } as any;
      const state = {
        getOptions: vi.fn(() => ({ padding: 20 }) as any),
      } as any;

      const instance = new ZoomWheel();
      instance.init({
        emitter: {} as any,
        editor: { getDocument: () => svg } as any,
        commander,
        interaction,
        state,
      });

      const event = new WheelEvent('wheel', { deltaY: -120, ctrlKey: true });
      document.dispatchEvent(event);

      expect(commander.execute).toHaveBeenCalledTimes(1);
      const command = commander.execute.mock.calls[0][0] as UpdateOptionsCommand;
      // 20 * 0.9 = 18
      expect(command.serialize().options).toEqual({
        padding: [18, 18, 18, 18],
      });

      instance.destroy();
    });

    it('zooms out from negative padding', () => {
      const svg = createSVG(100, 50);
      const commander = { execute: vi.fn() } as any;
      const interaction = { isActive: vi.fn(() => true) } as any;
      const state = {
        getOptions: vi.fn(() => ({ padding: -20 }) as any),
      } as any;

      const instance = new ZoomWheel();
      instance.init({
        emitter: {} as any,
        editor: { getDocument: () => svg } as any,
        commander,
        interaction,
        state,
      });

      const event = new WheelEvent('wheel', { deltaY: -120, ctrlKey: true });
      document.dispatchEvent(event);

      expect(commander.execute).toHaveBeenCalledTimes(1);
      const command = commander.execute.mock.calls[0][0] as UpdateOptionsCommand;
      // -20 * 0.9 = -18
      expect(command.serialize().options).toEqual({
        padding: [-18, -18, -18, -18],
      });

      instance.destroy();
    });
  });

  describe('modifier keys', () => {
    it('works with Ctrl key', () => {
      const svg = createSVG(100, 50);
      const commander = { execute: vi.fn() } as any;
      const interaction = { isActive: vi.fn(() => true) } as any;
      const state = {
        getOptions: vi.fn(() => ({ padding: 0 }) as any),
      } as any;

      const instance = new ZoomWheel();
      instance.init({
        emitter: {} as any,
        editor: { getDocument: () => svg } as any,
        commander,
        interaction,
        state,
      });

      const event = new WheelEvent('wheel', { deltaY: 120, ctrlKey: true });
      document.dispatchEvent(event);

      expect(commander.execute).toHaveBeenCalledTimes(1);
      instance.destroy();
    });

    it('works with Meta key (Cmd on Mac)', () => {
      const svg = createSVG(100, 50);
      const commander = { execute: vi.fn() } as any;
      const interaction = { isActive: vi.fn(() => true) } as any;
      const state = {
        getOptions: vi.fn(() => ({ padding: 0 }) as any),
      } as any;

      const instance = new ZoomWheel();
      instance.init({
        emitter: {} as any,
        editor: { getDocument: () => svg } as any,
        commander,
        interaction,
        state,
      });

      const event = new WheelEvent('wheel', { deltaY: 120, metaKey: true });
      document.dispatchEvent(event);

      expect(commander.execute).toHaveBeenCalledTimes(1);
      instance.destroy();
    });

    it('does not zoom without modifier keys', () => {
      const svg = createSVG(100, 50);
      const commander = { execute: vi.fn() } as any;
      const interaction = { isActive: vi.fn(() => true) } as any;
      const state = {
        getOptions: vi.fn(() => ({ padding: 0 }) as any),
      } as any;

      const instance = new ZoomWheel();
      instance.init({
        emitter: {} as any,
        editor: { getDocument: () => svg } as any,
        commander,
        interaction,
        state,
      });

      const event = new WheelEvent('wheel', { deltaY: 120 });
      document.dispatchEvent(event);

      expect(commander.execute).not.toHaveBeenCalled();
      instance.destroy();
    });
  });

  describe('interaction state', () => {
    it('does not zoom when interaction is not active', () => {
      const svg = createSVG(100, 50);
      const commander = { execute: vi.fn() } as any;
      const interaction = { isActive: vi.fn(() => false) } as any;
      const state = {
        getOptions: vi.fn(() => ({ padding: 0 }) as any),
      } as any;

      const instance = new ZoomWheel();
      instance.init({
        emitter: {} as any,
        editor: { getDocument: () => svg } as any,
        commander,
        interaction,
        state,
      });

      const event = new WheelEvent('wheel', { deltaY: 120, ctrlKey: true });
      document.dispatchEvent(event);

      expect(commander.execute).not.toHaveBeenCalled();
      instance.destroy();
    });
  });

  describe('boundary conditions', () => {
    it('prevents zoom when resulting viewbox would be too small (zoom out)', () => {
      const svg = createSVG(100, 100);
      const commander = { execute: vi.fn() } as any;
      const interaction = { isActive: vi.fn(() => true) } as any;
      const state = {
        getOptions: vi.fn(() => ({
          padding: [-100, -100, -100, -100],
        })) as any,
      } as any;

      const instance = new ZoomWheel();
      instance.init({
        emitter: {} as any,
        editor: { getDocument: () => svg } as any,
        commander,
        interaction,
        state,
      });

      const event = new WheelEvent('wheel', { deltaY: -120, ctrlKey: true });
      const preventDefaultSpy = vi.spyOn(event, 'preventDefault');
      document.dispatchEvent(event);

      expect(preventDefaultSpy).toHaveBeenCalled();
      expect(commander.execute).not.toHaveBeenCalled();

      instance.destroy();
    });

    it('prevents zoom when resulting viewbox width would be too small', () => {
      const svg = createSVG(10, 100);
      const commander = { execute: vi.fn() } as any;
      const interaction = { isActive: vi.fn(() => true) } as any;
      const state = {
        getOptions: vi.fn(() => ({
          padding: [-5, -5, -5, -5],
        })) as any,
      } as any;

      const instance = new ZoomWheel();
      instance.init({
        emitter: {} as any,
        editor: { getDocument: () => svg } as any,
        commander,
        interaction,
        state,
      });

      const event = new WheelEvent('wheel', { deltaY: -120, ctrlKey: true });
      document.dispatchEvent(event);

      // 10 + (-5 * 0.9) * 2 = 10 - 9 = 1, which is <= MIN_VIEWBOX_SIZE
      expect(commander.execute).not.toHaveBeenCalled();

      instance.destroy();
    });

    it('prevents zoom when resulting viewbox height would be too small', () => {
      const svg = createSVG(100, 10);
      const commander = { execute: vi.fn() } as any;
      const interaction = { isActive: vi.fn(() => true) } as any;
      const state = {
        getOptions: vi.fn(() => ({
          padding: [-5, -5, -5, -5],
        })) as any,
      } as any;

      const instance = new ZoomWheel();
      instance.init({
        emitter: {} as any,
        editor: { getDocument: () => svg } as any,
        commander,
        interaction,
        state,
      });

      const event = new WheelEvent('wheel', { deltaY: -120, ctrlKey: true });
      document.dispatchEvent(event);

      // 10 + (-5 * 0.9) * 2 = 10 - 9 = 1, which is <= MIN_VIEWBOX_SIZE
      expect(commander.execute).not.toHaveBeenCalled();

      instance.destroy();
    });
  });

  describe('edge cases', () => {
    it('handles undefined padding', () => {
      const svg = createSVG(100, 50);
      const commander = { execute: vi.fn() } as any;
      const interaction = { isActive: vi.fn(() => true) } as any;
      const state = {
        getOptions: vi.fn(() => ({ padding: undefined }) as any),
      } as any;

      const instance = new ZoomWheel();
      instance.init({
        emitter: {} as any,
        editor: { getDocument: () => svg } as any,
        commander,
        interaction,
        state,
      });

      const event = new WheelEvent('wheel', { deltaY: 120, ctrlKey: true });
      document.dispatchEvent(event);

      expect(commander.execute).toHaveBeenCalledTimes(1);
      const command = commander.execute.mock.calls[0][0] as UpdateOptionsCommand;
      // undefined padding defaults to 0, so should use initial value
      expect(command.serialize().options).toEqual({
        padding: [11, 11, 11, 11],
      });

      instance.destroy();
    });

    it('does not zoom when deltaY is zero (no scrolling)', () => {
      const svg = createSVG(100, 50);
      const commander = { execute: vi.fn() } as any;
      const interaction = { isActive: vi.fn(() => true) } as any;
      const state = {
        getOptions: vi.fn(() => ({ padding: 20 }) as any),
      } as any;

      const instance = new ZoomWheel();
      instance.init({
        emitter: {} as any,
        editor: { getDocument: () => svg } as any,
        commander,
        interaction,
        state,
      });

      const event = new WheelEvent('wheel', { deltaY: 0, ctrlKey: true });
      const preventDefaultSpy = vi.spyOn(event, 'preventDefault');
      document.dispatchEvent(event);

      // deltaY === 0 means no actual scrolling, so no zoom should occur
      expect(preventDefaultSpy).not.toHaveBeenCalled();
      expect(commander.execute).not.toHaveBeenCalled();

      instance.destroy();
    });
  });
});
