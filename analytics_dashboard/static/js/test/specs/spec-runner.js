var context = require.context('../../../', true, /.+spec\.jsx?$/);
require('../../load/init-tooltips.js');
require('axe-core');
context.keys().forEach(context);
module.exports = context;
