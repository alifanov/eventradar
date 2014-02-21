var _ = require('underscore');
var arr = [[1,2,3,4,5,1],[1,2,3,6,7,8]];
console.log(_.uniq(_.flatten(arr)));