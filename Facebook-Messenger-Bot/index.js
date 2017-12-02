'use strict'

const VERIFY_TOKEN = 'allonsy'
const API_KEY='2f77d7e61e6962a55a93c88383cc9b75'
const token = 'EAAB6uiRvoZBMBAI1iIxQwvCZB65QZAdmsYgsOToj82fkB8xBQVAP7lqZA3vmJ4GIeA0gBVdmr5ZCrimj7ugPnkcGArFduZApIJqeqy9pjzV7TtWrZAte24OxHNyfAizVMlhZBfTDsoDARVMH9T2JLZAFFhh8L28BCOb5vZAsxt6hMPOvZAK3kFYdD1m'
const express = require('express')
const bodyParser = require('body-parser')
const request = require('request')
const app = express()

app.set('port', (process.env.PORT || 5000))

// Process application/x-www-form-urlencoded
app.use(bodyParser.urlencoded({extended: false}))

// Process application/json
app.use(bodyParser.json())

// Index route
app.get('/', function (req, res) {
	res.send(VERIFY_TOKEN)
})

// for Facebook verification
app.get('/webhook/', function (req, res) {
	if (req.query['hub.verify_token'] === 'allonsy') {
		res.send(req.query['hub.challenge'])
	}
	res.send('Error, wrong token')
})

// Spin up the server
app.listen(app.get('port'), function() {
	console.log('running on port', app.get('port'))
})

app.post('/webhook/', function (req, res) {
    let messaging_events = req.body.entry[0].messaging
    for (let i = 0; i < messaging_events.length; i++) {
	    let event = req.body.entry[0].messaging[i]
	    let sender = event.sender.id

	    if (event.message && event.message.text && sender != myID) {
	    	let text = event.message.text
			request({
			    url: 'https://cc-chatbot.herokuapp.com/prediction',
			    method: 'POST',
			    body: {message: text.substring(0, 200)},
			    headers: {'User-Agent': 'request'},
				json: true 
			}, function(error, response, body) {
				sendTextMessage(sender, response.body)
			})
	    }
    }
    res.sendStatus(200)
})

function sendTextMessage(sender, text) {
    let messageData = { text:text }
    request({
	    url: 'https://graph.facebook.com/v2.6/me/messages',
	    qs: {access_token:token},
	    method: 'POST',
		json: {
		    recipient: {id:sender},
			message: messageData,
		}
	}, function(error, response, body) {
		if (error) {
		    console.log('Error sending messages: ', error)
		} else if (response.body.error) {
		    console.log('Error: ', response.body.error)
	    }
    })
}
