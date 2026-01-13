export default {
  presets: [
    ['@babel/preset-env', { targets: { node: 'current' } }],
    ['@babel/preset-react', { runtime: 'automatic' }],
  ],
  plugins: [
    // Transform import.meta.env for Jest compatibility
    function () {
      return {
        visitor: {
          MemberExpression(path) {
            // Match import.meta.env pattern
            if (
              path.node.object.type === 'MetaProperty' &&
              path.node.object.meta.name === 'import' &&
              path.node.object.property.name === 'meta' &&
              path.node.property.name === 'env'
            ) {
              // Replace import.meta.env with process.env
              path.replaceWithSourceString('process.env');
            }
          },
        },
      };
    },
  ],
};
