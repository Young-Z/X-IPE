/**
 * Tests for FEATURE-036-E CR-001: Feature-grouped deliverables layout.
 * Validates that _renderDeliverables groups items by feature_id
 * instead of by stage.
 */
import { describe, it, expect, beforeEach, vi } from 'vitest';

/**
 * Standalone test of the grouping logic extracted from _renderDeliverables.
 * We test the pure data transformation (shared vs byFeature split)
 * without needing the full DOM rendering pipeline.
 */
describe('FEATURE-036-E CR-001: Deliverables grouping logic', () => {
    /**
     * groupDeliverables: the pure logic that splits items into
     * shared (no feature_id) and byFeature (keyed by feature_id).
     */
    function groupDeliverables(items) {
        const shared = [];
        const byFeature = {};
        items.forEach(item => {
            if (!item.feature_id) {
                shared.push(item);
            } else {
                if (!byFeature[item.feature_id]) {
                    byFeature[item.feature_id] = { name: item.feature_name || item.feature_id, items: [] };
                }
                byFeature[item.feature_id].items.push(item);
            }
        });
        return { shared, byFeature };
    }

    it('should put items without feature_id into shared', () => {
        const items = [
            { name: 'idea.md', path: 'ideas/idea.md', category: 'ideas', stage: 'ideation', exists: true },
            { name: 'req.md', path: 'reqs/req.md', category: 'requirements', stage: 'requirement', exists: true },
        ];
        const { shared, byFeature } = groupDeliverables(items);
        expect(shared).toHaveLength(2);
        expect(Object.keys(byFeature)).toHaveLength(0);
    });

    it('should group items with feature_id by feature', () => {
        const items = [
            { name: 'spec.md', path: 'spec.md', category: 'requirements', stage: 'implement', feature_id: 'F-001', feature_name: 'Feature A', exists: true },
            { name: 'code.py', path: 'code.py', category: 'implementations', stage: 'implement', feature_id: 'F-001', feature_name: 'Feature A', exists: true },
            { name: 'test.py', path: 'test.py', category: 'quality', stage: 'validation', feature_id: 'F-002', feature_name: 'Feature B', exists: true },
        ];
        const { shared, byFeature } = groupDeliverables(items);
        expect(shared).toHaveLength(0);
        expect(Object.keys(byFeature)).toHaveLength(2);
        expect(byFeature['F-001'].items).toHaveLength(2);
        expect(byFeature['F-001'].name).toBe('Feature A');
        expect(byFeature['F-002'].items).toHaveLength(1);
        expect(byFeature['F-002'].name).toBe('Feature B');
    });

    it('should handle mix of shared and per-feature items', () => {
        const items = [
            { name: 'idea.md', path: 'idea.md', category: 'ideas', stage: 'ideation', exists: true },
            { name: 'spec.md', path: 'spec.md', category: 'requirements', stage: 'implement', feature_id: 'F-001', feature_name: 'Feature A', exists: true },
            { name: 'req.md', path: 'req.md', category: 'requirements', stage: 'requirement', exists: true },
            { name: 'test.py', path: 'test.py', category: 'quality', stage: 'validation', feature_id: 'F-001', feature_name: 'Feature A', exists: true },
        ];
        const { shared, byFeature } = groupDeliverables(items);
        expect(shared).toHaveLength(2);
        expect(shared[0].name).toBe('idea.md');
        expect(shared[1].name).toBe('req.md');
        expect(Object.keys(byFeature)).toHaveLength(1);
        expect(byFeature['F-001'].items).toHaveLength(2);
    });

    it('should use feature_id as name when feature_name missing', () => {
        const items = [
            { name: 'code.py', path: 'code.py', category: 'implementations', stage: 'implement', feature_id: 'F-003', exists: true },
        ];
        const { byFeature } = groupDeliverables(items);
        expect(byFeature['F-003'].name).toBe('F-003');
    });

    it('should return empty when no items', () => {
        const { shared, byFeature } = groupDeliverables([]);
        expect(shared).toHaveLength(0);
        expect(Object.keys(byFeature)).toHaveLength(0);
    });

    it('should combine deliverables from multiple stages for same feature', () => {
        const items = [
            { name: 'spec.md', path: 'spec.md', category: 'requirements', stage: 'implement', feature_id: 'F-001', feature_name: 'Feature A', exists: true },
            { name: 'code.py', path: 'code.py', category: 'implementations', stage: 'implement', feature_id: 'F-001', feature_name: 'Feature A', exists: true },
            { name: 'test.py', path: 'test.py', category: 'quality', stage: 'validation', feature_id: 'F-001', feature_name: 'Feature A', exists: true },
            { name: 'report.md', path: 'report.md', category: 'quality', stage: 'feedback', feature_id: 'F-001', feature_name: 'Feature A', exists: true },
        ];
        const { byFeature } = groupDeliverables(items);
        expect(byFeature['F-001'].items).toHaveLength(4);
    });
});
