const electron = require('electron');
const url = require('url');
const path = require('path');
const https = require('https');

const {app, BrowserWindow, Menu, ipcMain} = electron;
let mainWindow;
let addWindow;
let loginWindow;
//listen for app to be ready
app.on('ready', function(){
    //create new window
    mainWindow = new BrowserWindow({});
    //load html window
    mainWindow.loadURL(url.format({
        pathname: path.join(__dirname, 'mainWindow.html'),
        protocol: 'file:',
        slahes: true
    }));
    //Quit app when closed
    mainWindow.on('closed', function() {
        app.quit();
    });
    //build menu from template
    const mainMenu = Menu.buildFromTemplate(mainMenuTemplate);
    //insert menu
    Menu.setApplicationMenu(mainMenu);
});
//Handle create log in window

function createLoginWindow(){
    //create new window
    loginWindow = new BrowserWindow({
        width: 300, 
        height: 200, 
        title: 'Log in'
    });
    //load html window
    loginWindow.loadURL(url.format({
        pathname: path.join(__dirname, 'login.html'),
        protocol: 'file:',
        slahes: true
    }));
    //Garbage collection handle
    loginWindow.on('close', function(){
        loginWindow = null;
    });
}

//Handle create add window
function createAddWindow(){
    //create new window
    addWindow = new BrowserWindow({
        width: 300, 
        height: 200, 
        title: 'Register user'
    });
    //load html window
    addWindow.loadURL(url.format({
        pathname: path.join(__dirname, 'addWindow.html'),
        protocol: 'file:',
        slahes: true
    }));
    //Garbage collection handle
    addWindow.on('close', function(){
        addWindow = null;
    });
}
//catch register:user
ipcMain.on('register:user', function(e, user){
    console.log(user);
    addWindow.webContents.send('register:user', user);
    addWindow.close();
});
//catch login:user
ipcMain.on('login:user', function(e, user){
    console.log(user);
    mainWindow.webContents.send('login:user', user);
    loginWindow.close();
});
//Catch item:add
ipcMain.on('item:add', function(e, item){
    console.log(item);
    mainWindow.webContents.send('item:add', item);
    addWindow.close();
});
//create menu template
const mainMenuTemplate = [
    {
        label:'File',
        submenu:[
            {
                label: 'Register',
                click(){
                    createAddWindow();
                }
            },
            {
                label: 'Log in',
                click(){
                    createLoginWindow();
                }
            },
            {
                label: 'Quit',
                click(){
                    app.quit();
                }
            }
        ]
    }
];

//if mac, add empty object to menu
if(process.platform == 'darwin') {
    mainMenuTemplate.unshift({});
}
//Add developer tools item if not in prod
if(process.env.NODE_ENV !== 'production'){
    mainMenuTemplate.push({
        label: 'Developer Tools', 
        submenu:[
            {
                label: 'Toggle DevTools', 
                accelerator: process.platform == 'darwin' ? 'Command + I' : 
                'Ctrl+I',
                click(item, focusedWindow){
                    focusedWindow.toggleDevTools();
                }
            },
            {
                role: 'reload'
            }
        ]
    });
}