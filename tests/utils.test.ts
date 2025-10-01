import { describe, it, expect } from 'vitest';
import { formatPrice, formatDuration, formatDistance } from '../src/utils';

describe('Utils', () => {
  describe('formatPrice', () => {
    it('should format price correctly', () => {
      expect(formatPrice(123.45)).toBe('₹123');
      expect(formatPrice(99.99, '$')).toBe('$100');
    });
  });

  describe('formatDuration', () => {
    it('should format duration correctly', () => {
      expect(formatDuration(30)).toBe('Now');
      expect(formatDuration(60)).toBe('1 min');
      expect(formatDuration(300)).toBe('5 mins');
    });
  });

  describe('formatDistance', () => {
    it('should format distance correctly', () => {
      expect(formatDistance(500)).toBe('500m');
      expect(formatDistance(1500)).toBe('1.5km');
    });
  });
});
