const { io } = require("socket.io-client")
const fs = require('fs')

const socket = io("https://kit.digitalauto.tech");

/*
 * store all KITs information
 */
let kitArray = []

function msleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

// print process.argv
const args = process.argv;
if (args.length < 8) {
    console.log("Error: not enough params.\nSyntax: node main.js kit_id execType fileName filePath codeName codePath");
    process.exit(0);
}

let g_is_kit_registered = false
let g_kit_online = false
let g_kit_id = args[2];
let g_execType = args[3];
let g_appName = args[4];
let g_appPath = args[5];
let g_codeName = args[6];
let g_codePath = args[7];
console.log("g_kit_id : " + g_kit_id);
console.log("g_execType : " + g_execType);
console.log("g_fileName : " + g_appName);
console.log("g_appPath : " + g_appPath);
console.log("g_codeName : " + g_codeName);
console.log("g_codePath : " + g_codePath);

fs.readFile(g_appPath, (err, content) => {
    if (err) {
        console.log("read file failed : " + g_appPath);
        throw err;
        process.exit(0);
    }
});

fs.readFile(g_codePath, (err, content) => {
    if (err) {
        console.log("read file failed : " + g_codePath);
        throw err;
        process.exit(0);
    }
});

/*
 * Socket IO: on-connect to server
 */
socket.on("connect", () => {
    console.log("Socket connected !!!");
    socket.emit("register_client", {
        username: "etas_user1",
        user_id: "etas_user1",
        domain: "domain"
    });
    console.log("register done !!!");

    deployAraAppToKit(g_kit_id.toString(), g_execType.toString(),
        g_appName.toString(), g_appPath.toString(),
        g_codeName.toString(), g_codePath.toString());
});

/*
 * Socket IO: on-disconnected to server
 */
socket.on("disconnected", () => {
    console.log("socket disconnected !!!");
});

/*
 * Socket IO: on-list-all-kits-result. list of KIT info sent from Server
 */
socket.on("list-all-kits-result", (data) => {
    console.log("list-all-kits-result");
    // console.log(data);
    if (!data) {
        console.log("list-all-kits-result: null data");
    }
    kitArray = data
    for (var i = 0; i < data.length; i++) {
        let dataItem = kitArray[i];
        if (dataItem.name == g_kit_id) {
            g_is_kit_registered = true;
            console.log(dataItem.name + " online status is " + dataItem.is_online);
            if (dataItem.is_online) {
                g_kit_online = true;
            }
            else {
                g_kit_online = false;
            }
        }
    }
});

/*
 * Socket IO: on-messageToKit-kitReply: message replied from Server
 */
const onKitReply = (payload) => {
    if (!payload) {
        console.log("onKitReply: null payload");
        return
    }
    console.log("payload: ");
    console.log(payload);
    if (payload.cmd == "deploy_AraApp_Request") {
        if (payload.result == "success") {
            console.log("Sent araApp.\nHave fun with your Adaptive Application on dreamKIT !!!");
            process.exit(0);
        }
        else {
            console.log("Error: deployment failed !!!");
            process.exit(0);
        }
    }
}
socket.on("messageToKit-kitReply", onKitReply)

/*
 * calculate hash from string
 */
function stringToHash(string) {

    let hash = 0;

    if (string.length == 0) return hash;

    for (i = 0; i < string.length; i++) {
        char = string.charCodeAt(i);
        hash = ((hash << 5) - hash) + char;
        hash = hash & hash;
    }

    return hash;
}

/*
 * Send adaptive app to the kit
 */
function deployAraAppToKit(kit_id, execType, appName, appPath, codeName, codePath) {
    // fileType: cpp, py, js, etc.,

    let id_ = stringToHash("ara_" + appName);
    console.log("id_: " + id_);
    console.log("kit_id: " + kit_id);

    let code_content;
    fs.readFile(codePath, (err, buf) => {
        if (err) {
            console.log("read file failed : " + codePath);
            throw err;
            process.exit(-1);
        }
        code_content = buf;
    });
    // let appContent;
    fs.readFile(appPath, (err, buf) => {
        if (err) {
            console.log("read file failed : " + appPath);
            throw err;
        }
        console.log("file size = " + buf.length);
        console.log("file is OK. Let's send !");

        let p_payload = {
            cmd: "deploy_AraApp_Request",
            to_kit_id: kit_id,
            data: {
                deployFrom: "ETAS",
                id: id_.toString(),
                execType: execType,
                appName: appName,
                appContent: buf.toString('binary'),
                codeName: codeName,
                codeContent: code_content.toString(),
                run_after_deploy: false
            }
        }
        // let g_codeName = args[6];
        // let g_codePath = args[7];

        socket.emit("messageToKit", p_payload);
    });
}

/*
 * Send message to the kit
 */
function exeCmdOnKit(command, kit_id, cmdName) {
    let p_payload = {
        cmd: command,
        to_kit_id: kit_id,
        data: {
            cmd: cmdName,
        }
    }
    socket.emit("messageToKit", p_payload);
}