// postcss.config.js
import cssnano from 'cssnano';

export default {
  map: false, // Ensure no source maps
  plugins: [
    cssnano({
      preset: ['default', {
        discardComments: { removeAll: true },
        reduceIdents: true,
        mergeLonghand: true,
        normalizeWhitespace: true,
      }],
    }),
  ],
};
