var passport = require('passport');
var request = require('request');
var redis = require("redis"),
    client = redis.createClient();

var User = require('../models/users').User;

var async = require('async');

module.exports = function (app) {

    app.get('/sign-out', function (req, res) {
        req.logout();
        res.redirect('/');
    });
    app.get('/auth/vk',
        passport.authenticate('vk', {
            scope: ['groups']
        }),
        function (req, res) {
            // The request will be redirected to vk.com
            // for authentication, so
            // this function will not be called.
        });

    app.get('/auth/vk/callback',
        passport.authenticate('vk', {
            failureRedirect: '/'
        }),
        function (req, res) {
            // Successful authentication
            // save friends uid in redis
            request.get('https://api.vk.com/method/friends.get?uid='+req.user.uid, function(err,res, body)
            {
                body = JSON.parse(body);
                if ('response' in body)
                {
                    client.sadd('uid_'+req.user.uid, body.response);
                    User.findOrCreate({
                        username: req.user.username,
                        uid: req.user.uid,
                        friends: body.response,
                        access_token: req.user.access_token
                    });
                }
            });
            //, redirect home.
            res.redirect('/');
        });
}