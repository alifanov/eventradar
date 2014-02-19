var fs = require('fs');
var url = require('url');
var https = require('https');
var async = require('async');
var request = require('request');
var redis = require("redis"),
    client = redis.createClient();
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


fs.readFile('urls.txt', function(err, logData)
{
    request.get('https://api.vk.com/method/friends.get?uid='+vkid, function(err, response, body){
        var b = JSON.parse(body);
        uids = body.response;
        var uids_urls = _.map(uids, function(uid){
            client.setnx('uid_'+uid);
            console.log('Set uid: '+uid);
            return 'https://api.vk.com/method/friends.get?uid='+uid;
        });
        async.map(uids_urls, fetch, function(err, res)
        {
            for(i in res)
            {
                var raw_resp = JSON.parse(res[i]);
                if ('response' in raw_resp)
                {
                    _.map(raw_resp.response, function(uid)
                    {
                        client.setnx('uid_'+uid);
                    });
                }
            }
        });
    });

    client.keys('uid_*', function(err, res)
    {
        console.log(res.length)
    });
/*
    if (err) throw err;

    var text = logData.toString();


    var urls = text.split('\n');
    console.log('Count: '+urls.length);
    urls = objectDeDup(urls);
    console.log('Count of uniq: '+urls.length);
    urls = urls.slice(0, 40);
    nums = urls.length;

    console.log('Count fo urls: ' + urls.length);


    async.map(urls, fetch, function(err, results){
        if ( err){
        } else {
            for(i in results)
            {
                var data = JSON.parse(results[i]);
                if('response' in data)
                {
                    var posts = data.response.splice(1, 11)
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
//                                    console.log('[ today ' + d.toDateString() + ']: ' + posts[ii].text);
                                    good_post_count+=1;
                                }
                            }
                            if(posts[ii].text.match(tomorrow_exp))
                            {
                                var d = new Date(posts[ii].date*1000);
                                if (tomorrow.toDateString() == d.toDateString())
                                {
//                                    console.log('[ tomorrow ' + d.toDateString() + ']: ' + posts[ii].text);
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
                                        post_date: new Date(posts[ii].unixtime),
                                        event_date: d,
                                        text: posts[ii].text,
                                        source: posts[ii].to_id,
                                        link: 'https://vk.com/wall'+posts[ii].to_id + '_' + posts[ii].id
                                    };

                                    client.setnx(doc.link, JSON.stringify(doc));

                                    good_post_count+=1;
                                }

                            }
                        }
                    }
                }
            }
            client.quit();
            var diff = process.hrtime(time);
            console.log('DONE %d in %d sec %d nsec [Good: %d]', urls.length, diff[0], diff[1], good_post_count);
        }
    });
*/
    client.quit();
});