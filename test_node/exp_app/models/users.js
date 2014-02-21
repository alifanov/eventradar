var mongoose = require('mongoose');
var Schema = mongoose.Schema;
var findOrCreate = require('mongoose-findorcreate')

var User = new Schema({
    username: {type: String, required:true},
    uid: {type: Number, required: true},
    friends: [Number],
    access_token: {type: String}
});

var Source = new Schema({
    name: {type: String},
    uid: {type: Number},
    is_public: {type: Boolean}
});

var Post = new Schema({
    id: {type: String},
    post_date: {type: Date},
    event_date: {type: Date},
    text: {type: String},
    source: {type: String},
    link: {type: String}
});

User.plugin(findOrCreate);
Source.plugin(findOrCreate);

mongoose.connect('mongodb://localhost/test1');

module.exports.User = mongoose.model('User', User);
module.exports.Source = mongoose.model('Source', Source);
module.exports.Post = mongoose.model('Post', Post);