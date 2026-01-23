import { clamp } from 'lodash-es';
import type { Padding } from '../../types';
import { parsePadding } from '../../utils';
import { UpdateOptionsCommand } from '../commands';
import type { IInteraction, InteractionInitOptions } from '../types';
import { Interaction } from './base';

const MIN_VIEWBOX_SIZE = 1;
const MIN_PADDING = -5000;
const MAX_PADDING = 5000;
const ZOOM_IN_FACTOR = 1.1;
const ZOOM_OUT_FACTOR = 0.9;
// Initial padding value when current padding is 0
// This allows zooming to start from a reasonable base value
const INITIAL_PADDING_WHEN_ZERO = 10;

export class ZoomWheel extends Interaction implements IInteraction {
  name = 'zoom-wheel';

  private wheelListener = (event: WheelEvent) => {
    if (!this.interaction.isActive()) return;
    if (!event.ctrlKey && !event.metaKey) return;
    // Ignore events with zero deltaY (no actual scrolling)
    if (event.deltaY === 0) return;
    event.preventDefault();

    const isZoomIn = event.deltaY > 0;
    const factor = isZoomIn ? ZOOM_IN_FACTOR : ZOOM_OUT_FACTOR;
    const current = this.state.getOptions();
    const currentPadding = current.padding ?? 0;
    const parsed = parsePadding(currentPadding);
    const svg = this.editor.getDocument();
    const bbox = svg.getBBox();

    const scaled = parsed.map((value) => {
      // When padding is 0, use an initial value based on zoom direction
      // This provides a more intuitive zooming experience:
      // - Zoom in: start from a positive initial value (adds padding)
      // - Zoom out: start from a negative initial value (reduces viewbox)
      const baseValue =
        value === 0
          ? isZoomIn
            ? INITIAL_PADDING_WHEN_ZERO
            : -INITIAL_PADDING_WHEN_ZERO
          : value;
      return clamp(baseValue * factor, MIN_PADDING, MAX_PADDING);
    });

    const [top, right, bottom, left] = scaled;
    const newWidth = bbox.width + left + right;
    const newHeight = bbox.height + top + bottom;

    if (newWidth <= MIN_VIEWBOX_SIZE || newHeight <= MIN_VIEWBOX_SIZE) return;

    const command = new UpdateOptionsCommand({
      padding: scaled as Padding,
    });
    void this.commander.execute(command);
  };

  init(options: InteractionInitOptions) {
    super.init(options);
    document.addEventListener('wheel', this.wheelListener, { passive: false });
  }

  destroy() {
    document.removeEventListener('wheel', this.wheelListener);
  }
}
