import path from 'path';
import { fileURLToPath } from 'url';
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
export default (env, argv) => {
  const isProduction = argv.mode === 'production';
  return {
    mode: isProduction ? 'production' : 'development',
    entry: {
      tableForContracts: path.resolve(__dirname, './static/js/contracts_table.js'),
      tableForCompanies: path.resolve(__dirname, './static/js/companies_table.js'),
      tableForActs: path.resolve(__dirname, './static/js/acts_table.js'),
      tableForCategories: path.resolve(__dirname, './static/js/categories_table.js'),
      tableForAdditions: path.resolve(__dirname, './static/js/addition_table.js'),
      tablesForDashboard: path.resolve(__dirname, './static/js/dashboard_tables.js'),
      tableForUsers: path.resolve(__dirname, './static/js/users_table.js'),
    },
    output: {
      filename: '[name].bundle.js',
      path: path.resolve(__dirname, './static/js/'),
      // library: {
      //   type: 'module',
      // },
    },
    // experiments: {
    //   outputModule: true,
    // },
    resolve: {
      alias: {
        gridJs: path.resolve(__dirname, './node_modules/gridjs'),
      },
    },
    module: {
      rules: [
        {
          test: /\.css$/,
          use: ['style-loader', 'css-loader'],
        },
      ],
    },
    // Enable watch mode only in development
    watch: !isProduction,
    // Source maps for debugging
    devtool: isProduction ? 'source-map' : 'inline-source-map',
    // Optimization settings for production
    optimization: isProduction
      ? {
          // splitChunks: {
          //   chunks: 'all',
          // },
          minimize: true,
        }
      : {},
  };
};
