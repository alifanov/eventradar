var fs = require('fs');
var url = require('url');
var https = require('https');
var async = require('async');
var request = require('request');
var _ = require('underscore');

var vkid = '194484';

var time = process.hrtime();
var nums = 0;

var fetch = function(file,cb){
    request.get(file, function(err,response,body){
        if ( err){
            cb(err);
        } else {
            cb(null, body); // First param indicates error, null=> no error
        }
    });
};

var fetch_uid = function(file,cb){
    request.get(file, function(err,response,body){
        if ( err){
            cb(err);
        } else {
            var b = JSON.parse(body);
            cb(null, {'body': b.response, 'uid': file.split('uid=')[1]}); // First param indicates error, null=> no error
        }
    });
};

var date_exp = /(^|\s)([1-9]\d?\s(января|февраля|марта|апреля|мая|июня|июля|августа|сентября|октября|ноября|декабря))/mgi;

var months = {
    'января': 0,
    'февраля':1,
    'марта': 2,
    'апреля': 3,
    'мая': 4,
    'июня': 5,
    'июля': 6,
    'августа': 7,
    'сентября': 7,
    'октября': 9,
    'ноября': 10,
    'декабря': 11
};

var good_post_count = 0;

var objectDeDup = function(unordered) {
    var result = [];
    var object = {};
    unordered.forEach(function(item) {
        object[item] = null;
    });
    result = Object.keys(object);
    return result;
};

console.log('Getting uids');
    request.get('https://api.vk.com/method/friends.get?uid='+vkid, function(err, response, body){
        var b = JSON.parse(body);
        uids = b.response;
        var uids_urls = _.map(uids, function(uid){
//              client.sadd('uid_'+vkid, uid);
            return 'https://api.vk.com/method/friends.get?uid='+uid;
        });
        var diff = process.hrtime(time);

        console.log('Getting uids [DONE] in %d sec %d nsec', diff[0], diff[1]);
        console.log('Getting uids of uids');

        async.map(uids_urls.slice(0,40), fetch_uid, function(err, res)
        {
            res = _.pluck(res, 'body');
            console.log(res.length);
            var all_ids = _.uniq(_.flatten(res));
            console.log(all_ids.length);

            console.log('Getting uids of uids [DONE] in %d sec %d nsec', diff[0], diff[1]);

            console.log('Getting posts');

            client.keys('uid_*', function(err, res)
            {
                client.sunion(res, function(err, res)
                {
                    var uids_urls = _.map(res, function(uid)
                    {
                        return 'https://api.vk.com/method/wall.get?owner_id='+uid+'&count=10';
                    });
                    async.map(uids_urls.slice(0, 2000), fetch, function(err, results)
                    {
                        for(i in results)
                        {
                            var data = JSON.parse(results[i]);
                            if('response' in data)
                            {
                                var posts = data.response.splice(1, 11);
                                for(ii in posts)
                                {
                                    var today_exp = /(сегодня)/mgi;
                                    var tomorrow_exp = /(завтра)/mgi;
                                    if(posts[ii].text)
                                    {
                                        var today = new Date();
                                        var tomorrow = new Date(today.getTime() + 24 * 60 * 60 * 1000);

                                        if (posts[ii].text.match(today_exp))
                                        {
                                            var d = new Date(posts[ii].date*1000);
                                            if (d.toDateString() == today.toDateString())
                                            {
                                                var doc = {
                                                    id: posts[ii].to_id,
                                                    post_date: d,
                                                    event_date: today.setHours(0, 0, 0, 0),
                                                    text: posts[ii].text,
                                                    source: posts[ii].to_id,
                                                    link: 'https://vk.com/wall'+posts[ii].to_id + '_' + posts[ii].id
                                                };

//                                                client.sadd('wall_'+doc.id, JSON.stringify(doc), redis.print);
//                                                client.hset('walls', doc.id, JSON.stringify(doc));
                                                good_post_count+=1;
                                            }
                                        }
                                        if(posts[ii].text.match(tomorrow_exp))
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

//                                                client.sadd('wall_'+doc.id, JSON.stringify(doc), redis.print);
//                                                client.hset('walls', doc.id, JSON.stringify(doc));
                                                good_post_count+=1;
                                            }
                                        }
                                        if(posts[ii].text.match(date_exp))
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

//                                                client.sadd('wall_'+doc.id, JSON.stringify(doc), redis.print);
//                                                client.hset('walls', doc.id, JSON.stringify(doc));

                                                good_post_count+=1;
                                            }

                                        }
                                    }
                                }
                            }
                        }
                        console.log('Getting posts [DONE]');
                        var diff = process.hrtime(time);
                        console.log('DONE in %d sec %d nsec [Good: %d]', diff[0], diff[1], good_post_count);

                    });
                });
            });
        });
    });