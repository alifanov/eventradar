var redis = require("redis"),
    client = redis.createClient();

var request = require('request');
var dateformat = require('dateformat');
var truncate = require('html-truncate');

var User = require('../models/users').User;
var Source = require('../models/users').Source;
var Post = require('../models/users').Post;

var _ = require('underscore');

var sortPostsByDate = function (a, b)    {
    if (a.event_date < b.event_date) return -1;
    if (a.event_date > b.event_date) return 1;
    return 0;
};

/*************************** regular expression *********************/
var date_exp = /(^|\s)([1-9]\d?\s(января|февраля|марта|апреля|мая|июня|июля|августа|сентября|октября|ноября|декабря))/mgi;
var today_exp = /(сегодня)/mgi;
var tomorrow_exp = /(завтра)/mgi;

/********************************************************************/

client.on("error", function (err) {
    console.log("error event - " + client.host + ":" + client.port + " - " + err);
});

var getPosts = function(req, resp, cb){
    client.smembers('uid_'+req.user.uid, function(err, res)
    {
        var keys = _.map(res, function(n){
            return 'uid_'+n;
        });
        client.sunion(keys, function(err, res){
            var walls = client.hmget('walls', res, function(err,ress)
            {
                var posts = _.filter(ress, function(n){return n;});
                posts = _.map(posts, function(n){
                    var r = JSON.parse(n);
                    r.text = truncate(r.text, 300);
                    r.event_date = new Date(r.event_date);
                    r.event_date_human = dateformat(r.event_date, 'dd.mm.yyyy');
                    return r;
                });
                posts = posts.sort(sortPostsByDate);
                cb(posts);
            });
        });

    });
};

module.exports = function(app)
{
    app.get('/process/posts/', function(req, resp){
        Post.find(function(err, posts){
            resp.send(posts);
        });
        Source.find(function(err, sources){
            _.map(sources, function(source){
                request.get('https://api.vk.com/method/wall.get?owner_id='+source.uid+'&count=10',
                    function(err, resp, body){
                        var b = JSON.parse(body);
                        if('response' in b){
                            _.map(b.response.slice(1), function(post){
                                //process posts
                                if(post.text)
                                {
                                    if(post.text.match(date_exp))
                                    {
                                        var dat = posts[ii].text.match(date_exp)[0]
                                            .replace(/^\s/, '')
                                            .replace(/\s$/, '')
                                            .split(' ');
                                        var d = new Date(today.getFullYear(), months[dat[1]], dat[0]);
                                        if(d >= today.setHours(0, 0, 0, 0))
                                        {
                                            var doc = {
                                                id: posts[ii].to_id,
                                                post_date: posts[ii].date,
                                                event_date:d.getTime(),
                                                text: posts[ii].text,
                                                source: posts[ii].to_id,
                                                link: 'https://vk.com/wall'+posts[ii].to_id + '_' + posts[ii].id
                                            };
                                            Post.findOrCrate(doc);
                                        }
                                    }
                                    else
                                    {
                                        if(post.text.match(today_exp))
                                        {
                                            var d = new Date(posts[ii].date*1000);
                                            if (tomorrow.toDateString() == d.toDateString())
                                            {
                                                var doc = {
                                                    id: posts[ii].to_id,
                                                    post_date: d,
                                                    event_date: tomorrow.setHours(0, 0, 0, 0),
                                                    text: posts[ii].text,
                                                    source: posts[ii].to_id,
                                                    link: 'https://vk.com/wall'+posts[ii].to_id + '_' + posts[ii].id
                                                };

                                                Post.findOrCrate(doc);
                                            }
                                        }
                                        else
                                        {
                                            if(post.text.match(tomorrow_exp))
                                            {
                                                var dat = posts[ii].text.match(date_exp)[0]
                                                    .replace(/^\s/, '')
                                                    .replace(/\s$/, '')
                                                    .split(' ');
                                                var d = new Date(today.getFullYear(), months[dat[1]], dat[0]);
                                                if(d >= today.setHours(0, 0, 0, 0))
                                                {
                                                    var doc = {
                                                        id: posts[ii].to_id,
                                                        post_date: posts[ii].date,
                                                        event_date:d.getTime(),
                                                        text: posts[ii].text,
                                                        source: posts[ii].to_id,
                                                        link: 'https://vk.com/wall'+posts[ii].to_id + '_' + posts[ii].id
                                                    };

                                                    Post.findOrCreate(doc);

                                                }
                                            }
                                        }
                                    }
                                }
                            });
                        }
                    });
            });
        });
    });

    app.get('/process/sources/', function(req, resp){
        Source.find(function(err, sources){
            _.map(sources, function(source){
                request.get('https://api.vk.com/method/friends.get?uid='+source.uid+'&fields=first_name,last_name,uid',
                function(err, response, body){
                    var b = JSON.parse(body);
                    if('response' in b){
                        _.map(b.response, function(n){
                            Source.findOrCreate({
                                name: n.first_name + ' ' + n.last_name,
                                uid: n.uid,
                                is_public: false
                            }, function(err, source, created){});
                        });
                    }
                });
            });
            Source.find(function(err, sources){
                resp.send(sources);
            });
        });
    });

    app.get('/process/uids/', function(req, resp){
        User.find(function(err, users)
        {
            var sources = [];
            _.map(users, function(u)
            {
                //get friends
                request.get('https://api.vk.com/method/friends.get?uid='+ u.uid+'&fields=first_name,last_name,uid', function(err, response, body){
                    var b = JSON.parse(body);
                    if('response' in b)
                    {
                        _.map(b.response, function(n)
                        {
                            Source.findOrCreate({
                                name: n.first_name + ' ' + n.last_name,
                                uid: n.uid,
                                is_public: false
                            }, function(err, source, created){});
                        });
                    }
                });
            });
            Source.find(function(err, sources){
                resp.send(sources);
            });
        });
    });
    app.get('/users/', function(req, resp){
        User.find(function(err, users)
        {
            if(err)
            {
                resp.send(err);
            }
            else
            {
                resp.send(users);
            }
        });
    });
    app.get('/today/', function(req, resp){
        if(req.user)
        {
            getPosts(req, resp, function(posts)
            {
                var now = new Date();
                posts = _.filter(posts, function(n)
                {
                    return now.getDate() == new Date(n.event_date).getDate();
                });
                resp.render('index', {
                    current: 'today',
                    'user': req.user,
                    'posts': posts
                })
            });
        }
        else{
            resp.redirect('/');
        }
    });
    app.get('/tomorrow/', function(req, resp){
        if(req.user)
        {
            getPosts(req, resp, function(posts)
            {
                var now = new Date();
                var tomorrow = new Date(now.getTime()+24*60*60*1000);
                posts = _.filter(posts, function(n)
                {
                    return tomorrow.getDate() == new Date(n.event_date).getDate();
                });
                resp.render('index', {
                    current: 'tomorrow',
                    'user': req.user,
                    'posts': posts
                })
            });
        }
        else{
            resp.redirect('/');
        }
    });
    app.get('/week/', function(req, resp){
        if(req.user)
        {
            getPosts(req, resp, function(posts)
            {
                var now = new Date();
                var in_week = new Date(now.getTime()+8*24*60*60*1000);
                posts = _.filter(posts, function(n)
                {
                    return new Date(n.event_date) < in_week.setHours(0, 0, 0, 0);
                });
                resp.render('index', {
                    current: 'week',
                    'user': req.user,
                    'posts': posts
                })
            });
        }
        else{
            resp.redirect('/');
        }
    });
    app.get('/month/', function(req, resp){
        if(req.user)
        {
            getPosts(req, resp, function(posts)
            {
                var now = new Date();
                var in_month = new Date(now.getTime()+30*24*60*60*1000);
                posts = _.filter(posts, function(n)
                {
                    return new Date(n.event_date) < in_month.setHours(0, 0, 0, 0);
                });
                resp.render('index', {
                    current: 'month',
                    'user': req.user,
                    'posts': posts
                })
            });
        }
        else{
            resp.redirect('/');
        }
    });
    app.get('/', function(req, resp){
        // if authentifacted
        if(req.user)
        {
            // get keys from pattern
//            client.smembers('uid_'+req.user.uid, function(err, res)
//            {
//                var keys = _.map(res, function(n){
//                    return 'uid_'+n;
//                });
//                client.sunion(keys, function(err, res){
//                    var walls = client.hmget('walls', res, function(err,ress)
//                    {
//                        var posts = _.filter(ress, function(n){return n;});
//                        posts = _.map(posts, function(n){
//                            var r = JSON.parse(n);
//                            r.text = truncate(r.text, 300);
//                            r.event_date = new Date(r.event_date);
//                            r.event_date_human = dateformat(r.event_date, 'dd.mm.yyyy');
//                            return r;
//                        });
//                        posts = posts.sort(sortPostsByDate);
//                        resp.render('index',{
//                            'user': req.user,
//                            'posts': posts
//                        });
//                    });
//                });
//
//            });
            getPosts(req, resp, function(posts)
            {
                resp.render('index', {
                    'user': req.user,
                    'posts': posts
                });
            });
        }
        else
        {
            resp.render('index', {});
        }
    })
};
