var path = require("path")
var webpack = require('webpack')
var BundleTracker = require('webpack-bundle-tracker')

var config = require('./webpack.base.config.js')

// Add HotModuleReplacementPlugin and BundleTracker plugins
config.plugins = [
    new BundleTracker({filename: './webpack-stats.json'}),
],

module.exports = config