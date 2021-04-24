const mix = require('laravel-mix');
const rootPath = Mix.paths.root.bind(Mix.paths);
require('laravel-mix-purgecss');

mix//.js('js/app.js', '../static/assets/js')
    .postCss('css/app.css', '../web/static/assets/css')
    .options({
        postCss: [
            require('postcss-import')(),
            require('tailwindcss')('./tailwind.config.js'),
            require('postcss-nesting')(),
        ]
    })
    .purgeCss({
        content: [
            rootPath('public/**/*.html'), // edit me
        ],
        whitelistPatterns: [],
    });
