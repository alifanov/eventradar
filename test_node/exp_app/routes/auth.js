var passport = require('passport');
var request = require('request');
var redis = require("redis"),
    client = redis.createClient();

var async = require('async');

module.exports = function (app) {

    app.get('/sign-out', function (req, res) {
        req.logout();
        res.redirect('/');
    });
    app.get('/auth/vk',
        passport.authenticate('vk', {
            scope: ['offline']
        }),
        function (req, res) {
            // The request will be redirected to vk.com
            // for authentication, so
            // this function will not be called.
        });

    app.get('/auth/vk/callback',
        passport.authenticate('vk', {
            failureRedirect: '/auth'
        }),
        function (req, res) {
            // Successful authentication
            // save friends uid in redis
            request.get('https://api.vk.com/method/friends.get?uid='+req.user.uid, function(err,res, body)
            {
                body = JSON.parse(body);
                if ('response' in body)
                {
                    async.map(body.response, function(n)
                    {
                        client.sadd('uids_'+req.user.uid, n);
                    }, function(err, results){
                        client.end();
                    });
                }
            });
            //, redirect home.
            res.redirect('/');
        });
}