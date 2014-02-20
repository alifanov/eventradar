var redis = require("redis"),
    client = redis.createClient();

var _ = require('underscore');

client.on("error", function (err) {
    console.log("error event - " + client.host + ":" + client.port + " - " + err);
});

module.exports = function(app)
{
    app.get('/posts', function(req, resp){
        if(req.user)
        {
            console.log('Get uids of '+req.user.uid);
            client.smembers('uid_'+req.user.uid, function(err, res)
            {
                console.log('Get members');
                client.end();
                resp.render('index', {
                    'r': res
                });

                var keys = _.map(res, function(n){return 'uid_'+n});
                client.sunion(keys, function(err, res)
                {
                    console.log('Get union');
                    var walls = _.map(res, function(n){
                        return 'wall_'+n;
                    });
                    client.sunion(walls, function(err,res)
                    {
                        resp.render('index',{
                            'user': req.user,
                            'posts': res
                        })
                    });
                });
            });
        }
        else{
            resp.render('index', {});
        }
    });
    app.get('/', function(req, resp){
        // if authentifacted
        if(req.user)
        {
            // get keys from pattern
            client.smembers('uid_'+req.user.uid, function(err, res)
            {
                var keys = _.map(res, function(n){return 'uid_'+n});
                client.sunion(keys, function(err, res)
                {
                    var walls = _.map(res, function(n){
                        return 'wall_'+n;
                    });
                    var posts = [];
                    res.forEach(function(rep, i){
                        console.log('wall_'+rep);
                        client.get('wall_'+rep, function(err, res)
                        {
                            console.log(err);
                            posts = posts.concat(res);
                        });
                    });
                    client.SUNION(walls, function(err,res)
                    {
                        var posts = _.map(res, function(n){return JSON.parse(n)});
                        console.log(posts.length);
                        resp.render('index',{
                            'user': req.user,
                            'posts': posts
                        })
                    });
                });
            });
        }
        else
        {
            resp.render('index', {});
        }
    })
};
