const BundleTracker = require("webpack-bundle-tracker");

const pages = {
    'group_detail_vue': {
        entry: './src/group_detail_main.js',
        chunks: ['chunk-vendors']
    },
    'group_create_vue': {
        entry: './src/group_create_main.js',
        chunks: ['chunk-vendors']
    },
    'profile_vue': {
        entry: './src/profile_main.js',
        chunks: ['chunk-vendors']
    },
    'template_library': {
        entry: './src/template_library.js',
        chunks: ['chunk-vendors']
    }
}

module.exports = {
    pages: pages,
    css: {
        extract: true
      },
    filenameHashing: false,
    productionSourceMap: false,
    publicPath: process.env.NODE_ENV === 'production'
        ? ''
        : 'http://localhost:8080/',
    outputDir: '../static/vue/',

    chainWebpack: config => {

        config.optimization
            .splitChunks({
                cacheGroups: {
                    vendor: {
                        test: /[\\/]node_modules[\\/]/,
                        name: "chunk-vendors",
                        chunks: "all",
                        priority: 1
                    },
                },
            });

        Object.keys(pages).forEach(page => {
            config.plugins.delete(`html-${page}`);
            config.plugins.delete(`preload-${page}`);
            config.plugins.delete(`prefetch-${page}`);
        })

        config
            .plugin('BundleTracker')
            .use(BundleTracker, [{filename: '../frontend/webpack-stats.json'}]);

        config.resolve.alias
            .set('__STATIC__', 'static')

        config.devServer
            .public('http://localhost:8080')
            .host('localhost')
            .port(8080)
            .hotOnly(true)
            .watchOptions({poll: 1000})
            .https(false)
            .headers({"Access-Control-Allow-Origin": ["*"]})

    }
};