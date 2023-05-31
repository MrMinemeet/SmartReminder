const EXPRESS = require('express');
const MQTT = require('mqtt');
//const CLIENT = MQTT.connect('mqtt://localhost:8883');

const APP = EXPRESS();
const PORT =  8080;

app.use(express.urlencoded({ extended: false })); // Parse URL-encoded data in request body


APP.gepostt('/', (req, res) => {
	  res.send('Hello World!');
});

APP.get('/sendImage', (req, res) => {
	  res.send('sendImg');
	console.log(req.body)
	//CLIENT.publish('addImage', req.body.value);
});

APP.get('/addTask', (req, res) => {
	  res.send('addTask');
	//CLIENT.publish('addTask', req.body.value);
});

APP.get('/getTask', (req, res) => {
	  res.send('getTask');
	//CLIENT.publish('getTask', req.body.value);
});

APP.listen(PORT, () => {
	console.log(`Server listening on port ${PORT}`);
});

CLIENT.on('error', (error) => {
	console.error('Error:', error);
});
