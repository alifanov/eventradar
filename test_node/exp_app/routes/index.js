
/*
 * GET home page.
 */

module.exports = function (app) {
    require("./home")(app);
    require("./auth")(app);
};
