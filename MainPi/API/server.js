const EXPRESS = require('express');
const MQTT = require('mqtt');
const CLIENT = MQTT.connect('mqtt://main.local:1883');

const APP = EXPRESS();
const PORT =  8080;

APP.use(require('body-parser').text());
APP.use(EXPRESS.urlencoded({ extended: false })); // Parse URL-encoded data in request body
APP.use((req, res, next) => {
	console.log('---');
	console.log('New connection received');
	console.log('Method:', req.method);
	console.log('URL:', req.originalUrl);
	console.log('Timestamp:', new Date().toISOString());
	console.log('---');
  
	next();
});

APP.post('/addImage/:personName', (req, res) => {
	const image = req.body;
	const personName = req.params.personName;
	const jsonData = JSON.stringify({personName, image});
	res.status(200).send();
});

APP.post('/addTask', (req, res) => { 
	// Just send the recieved data over MQTT to the broker
	res.send('addTask ' + req.body);
	CLIENT.publish('addTask', req.body);
});

APP.get('/getTask', async (req, res) => {
	const taskId = req.query.id;
	CLIENT.subscribe('getTaskResponse');
	CLIENT.publish('getTask', taskId);
	// Await response from broker
	const response = await new Promise((resolve, reject) => {
		CLIENT.on('message', (topic, message) => {
			if (topic === 'getTaskResponse') {
				resolve(message.toString());
		  	}
		});
		setTimeout(() => {
		  reject(new Error('Timeout for getTaskResponse'));
		}, 5000); // Set a timeout of 5 seconds
	}).then((response) => {
		console.log('Response:', response);
		res.send(response);
	}).catch((error) => {
		console.error(error.message);
		res.status(504).send(error.message);
	}).finally(() => {
		CLIENT.unsubscribe('getTaskResponse');
	});
});

APP.get('/getData/:personName/:date', async (req, res) => {
	const personName = req.params.personName;
	const date = req.params.date;
	CLIENT.subscribe('getDataResponse');
	CLIENT.publish('getData', JSON.stringify({personName, date}));
	const response = await new Promise((resolve, reject) => {
		CLIENT.on('message', (topic, message) => {
			if (topic === 'getDataResponse') {
				resolve(message.toString());
		  	} 
		});
		setTimeout(() => {
		  reject(new Error('Timeout for getDataResponse'));
		}, 5000); // Set a timeout of 5 seconds
	}).then((response) => {
		console.log('Response:', response);
		res.send(response);
	}).catch((error) => {
		console.error(error.message);
		res.status(504).send(error.message);
	}).finally(() => {
		CLIENT.unsubscribe('getDataResponse');
	});
});

APP.get('/getAllPeople', async (req, res) => {
	CLIENT.subscribe('getAllPeopleResponse');
	CLIENT.publish('getAllPeople', '');
	const response = await new Promise((resolve, reject) => {
		CLIENT.on('message', (topic, message) => {
			if (topic === 'getAllPeopleResponse') {
				resolve(message.toString());
			}
		});
		setTimeout(() => {
			reject(new Error('Timeout for getAllPeopleResponse'));
		}, 5000); // Set a timeout of 5 seconds
	}).then((response) => {
		console.log('Response:', response);
		res.send(response);
	}).catch((error) => {
		console.error(error.message);
		res.status(504).send(error.message);
	}).finally(() => {
		CLIENT.unsubscribe('getAllPeopleResponse');
	});
});

APP.get('/removeTask/:id', async (req, res) => {
	const taskId = req.query.id;
	CLIENT.subscribe('removeTaskResponse');
	CLIENT.publish('removeTask', taskId);
	const response = await new Promise((resolve, reject) => {
		CLIENT.on('message', (topic, message) => {
			if (topic === 'removeTaskResponse') {
				resolve(message.toString());
			}
		});
		setTimeout(() => {
			reject(new Error('Timeout for removeTaskResponse'));
		}, 5000); // Set a timeout of 5 seconds
	}).then((response) => {
		console.log('Response:', response);
		res.send(response);
	}).catch((error) => {
		console.error(error.message);
		res.status(504).send(error.message);
	}).finally(() => {
		CLIENT.unsubscribe('removeTaskResponse');
	});
});

APP.listen(PORT, () => {
	console.log(`Server listening on port ${PORT}`);
});


CLIENT.on('error', (error) => {
	console.error('Error:', error);
});