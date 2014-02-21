var mongoose = require('mongoose');
var Schema = mongoose.Schema;
var findOrCreate = require('mongoose-findorcreate');
var request = require('request');
var async = require('async');
var _ = require('underscore');

var UserSchema = new Schema({
    username: {type: String, required:true},
    uid: {type: Number, required: true},
    friends: [Number],
    access_token: {type: String}
});

var SourceSchema = new Schema({
    name: {type: String},
    uid: {type: Number},
    is_public: {type: Boolean}
});

var PostSchema = new Schema({
    id: {type: String},
    post_date: {type: Date},
    event_date: {type: Date},
    text: {type: String},
    source: {type: String},
    link: {type: String}
});

UserSchema.plugin(findOrCreate);
SourceSchema.plugin(findOrCreate);
PostSchema.plugin(findOrCreate);

mongoose.connect('mongodb://localhost/test1');

var User = mongoose.model('User', UserSchema);
var Source = mongoose.model('Source', SourceSchema);
var Post = mongoose.model('Post', PostSchema);

var get_users = function(uid, cb){
   request.get('https://api.vk.com/method/friends.get?uid='+uid+'&fields=first_name,last_name,uid',
       function(err, response, body){
       if(err){
           cb(err);
       }
       else{
           var b = JSON.parse(body);
           if ('response' in b){
               cb(null, b.response);
           }
           else{
               cb(null, null);
           }
       }
   })
};

var get_posts = function(uid, cb)
{
    request.get('https://api.vk.com/method/wall.get?owner_id='+uid+'&count=10',
    function(err, response, body){
        var b = JSON.parse(body);
        if('response' in b)
        {
            cb(null, b.response);
        }
        else
        {
            cb(null, null);
        }
    })
};

var time = process.hrtime();

User.find(function(err, users){
    var keys = _.map(users, function(u){
        return u.uid;
    });
    //for every users collect uid posts
    async.map(keys, get_users, function(err, results){
        var uids = _.map(results, function(r){
            return _.pluck(r, 'uid');
        });
        uids = _.uniq(_.flatten(uids));
        console.log(uids.length);
        var diff = process.hrtime(time);
        console.log('Getting uids first wave [DONE] in %d sec %d nsec', diff[0], diff[1]);
        async.map(uids, get_users, function(err, results){
            var uids2 = _.map(results, function(r){
                console.log(r);
                return _.pluck(r,'uid');
            });
            uids2 = _.uniq(_.flatten(uids2));
            console.log(uids2.length);
            var diff = process.hrtime(time);
            console.log('Getting uids second wave [DONE] in %d sec %d nsec', diff[0], diff[1]);
            async.map(uids2.slice(20), get_posts, function(err, results)
            {
                var posts = _.flatten(results);
                console.log(posts.length);
                var diff = process.hrtime(time);
                console.log('Getting uids third wave [DONE] in %d sec %d nsec', diff[0], diff[1]);
            });
        });
        // TODO: get posts
        // TODO: check posts
        // TODO: save posts
        // TODO: save uids for user
    });
});
