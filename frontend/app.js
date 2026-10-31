const API = "/api";

let currentPage = "chat";

function getToken() {
    return localStorage.getItem("flaxxi_token");
}

function authHeaders() {
    return {
        "Authorization":"Bearer " + getToken()
    };
}

async function request(url, options={}) {

    const response = await fetch(API + url, {
        ...options,
        headers:{
            ...authHeaders(),
            ...(options.headers || {})
        }
    });

    const data = await response.json();

    if(!response.ok) {
        throw new Error(data.detail || "Request failed");
    }

    return data;
}


async function login() {

    const email = document.getElementById("email").value;

    const password = document.getElementById("password").value;

    try {

        const response = await fetch(API + "/login", {

            method:"POST",

            headers:{
                "Content-Type":"application/json"
            },

            body:JSON.stringify({email,password})

        });

        const data = await response.json();

        if(!response.ok) throw new Error(data.detail);

        localStorage.setItem("flaxxi_token",data.token);

        startApp();

    } catch(error) {

        document.getElementById("authStatus").textContent =
            error.message;

    }
}


async function register() {

    const email = document.getElementById("email").value;

    const password = document.getElementById("password").value;

    try {

        const response = await fetch(API + "/register", {

            method:"POST",

            headers:{
                "Content-Type":"application/json"
            },

            body:JSON.stringify({email,password})

        });

        const data = await response.json();

        if(!response.ok) throw new Error(data.detail);

        alert("Account created. Now login.");

    } catch(error) {

        document.getElementById("authStatus").textContent =
            error.message;

    }
}


function startApp() {

    document.getElementById("authScreen").classList.add("hidden");

    document.getElementById("dashboard").classList.remove("hidden");

    showPage("chat");

}


function logout() {

    localStorage.removeItem("flaxxi_token");

    location.reload();

}


function panel(title,html) {

    document.getElementById("title").textContent = title;

    document.getElementById("workspace").innerHTML =

        `<div class="panel">
            <h2>${title}</h2>
            ${html}
        </div>`;

}


function showPage(page) {

    currentPage = page;

    if(page === "chat") chatPage();

    if(page === "code") codePage();

    if(page === "image") imagePage();

    if(page === "apk") apkPage();

    if(page === "dex") dexPage();

    if(page === "history") historyPage();

}


// AI CHAT

function chatPage() {

    panel("FLAXXI AI CHAT",`

        <div id="chatMessages"></div>

        <textarea id="chatInput"
        placeholder="Ask anything..."></textarea>

        <button onclick="sendChat()">SEND ➤</button>

    `);

}


async function sendChat() {

    const input = document.getElementById("chatInput");

    const message = input.value.trim();

    if(!message) return;

    input.value = "";

    const messages = document.getElementById("chatMessages");

    const user = document.createElement("div");

    user.className = "message";

    user.textContent = "You: " + message;

    messages.appendChild(user);

    const ai = document.createElement("div");

    ai.className = "message";

    ai.textContent = "FLAXXI: Thinking...";

    messages.appendChild(ai);

    try {

        const data = await request("/chat",{

            method:"POST",

            headers:{
                "Content-Type":"application/json"
            },

            body:JSON.stringify({message})

        });

        ai.textContent = "FLAXXI: " + data.answer;

    } catch(error) {

        ai.textContent = error.message;

    }

}


// CODE GENERATOR

function codePage() {

    panel("AI CODE GENERATOR",`

        <textarea id="codePrompt"
        placeholder="Describe your project or code..."></textarea>

        <select id="codeLanguage">

            ${[
                "HTML","CSS","JavaScript","Python",
                "Java","Kotlin","JSON","XML",
                "C","C++","PHP","SQL",
                "TypeScript","Dart","Smali"
            ].map(x=>`<option>${x}</option>`).join("")}

        </select>

        <button onclick="generateCode()">GENERATE</button>

        <button onclick="downloadCode()">DOWNLOAD</button>

        <pre id="codeResult"></pre>

    `);

}


async function generateCode() {

    const prompt = document.getElementById("codePrompt").value;

    const language = document.getElementById("codeLanguage").value;

    const output = document.getElementById("codeResult");

    output.textContent = "Generating...";

    try {

        const data = await request("/generate-code",{

            method:"POST",

            headers:{
                "Content-Type":"application/json"
            },

            body:JSON.stringify({prompt,language})

        });

        output.textContent = data.code;

    } catch(error) {

        output.textContent = error.message;

    }

}


function downloadCode() {

    const code = document.getElementById("codeResult").textContent;

    if(!code || code === "Generating...") return;

    const language = document.getElementById("codeLanguage").value;

    const ext = {
        HTML:"html",CSS:"css",JavaScript:"js",
        Python:"py",Java:"java",Kotlin:"kt",
        JSON:"json",XML:"xml",C:"c","C++":"cpp",
        PHP:"php",SQL:"sql",TypeScript:"ts",
        Dart:"dart",Smali:"smali"
    };

    const blob = new Blob([code],{type:"text/plain"});

    const url = URL.createObjectURL(blob);

    const link = document.createElement("a");

    link.href = url;

    link.download = "flaxxi." + (ext[language] || "txt");

    link.click();

    URL.revokeObjectURL(url);

}


// IMAGE STUDIO

function imagePage() {

    panel("AI IMAGE STUDIO",`

        <p>Upload image and mask.</p>

        <input type="file" id="imageFile" accept="image/*">

        <input type="file" id="maskFile" accept="image/*">

        <textarea id="imagePrompt"
        placeholder="Describe image changes"></textarea>

        <button onclick="editImage()">EDIT IMAGE</button>

        <div id="imageResult"></div>

    `);

}


async function editImage() {

    const image = document.getElementById("imageFile").files[0];

    const mask = document.getElementById("maskFile").files[0];

    const prompt = document.getElementById("imagePrompt").value;

    if(!image || !mask || !prompt) {
        alert("Select image, mask and enter prompt");
        return;
    }

    const form = new FormData();

    form.append("image",image);

    form.append("mask",mask);

    form.append("prompt",prompt);

    const result = document.getElementById("imageResult");

    result.textContent = "Processing...";

    try {

        const data = await request("/edit-image",{
            method:"POST",
            body:form
        });

        const img = document.createElement("img");

        img.src = data.image_url;

        img.style.maxWidth = "100%";

        result.replaceChildren(img);

    } catch(error) {

        result.textContent = error.message;

    }

}


// APK ANALYZER

function apkPage() {

    panel("APK ANALYZER",`

        <input type="file" id="apkFile" accept=".apk">

        <button onclick="analyzeAPK()">ANALYZE APK</button>

        <button onclick="rebuildAPK()">REBUILD APK</button>

        <pre id="apkResult"></pre>

    `);

}


async function analyzeAPK() {

    const file = document.getElementById("apkFile").files[0];

    if(!file) return alert("Select APK");

    const form = new FormData();

    form.append("file",file);

    const output = document.getElementById("apkResult");

    output.textContent = "Analyzing...";

    try {

        const data = await request("/analyze-apk",{
            method:"POST",
            body:form
        });

        output.textContent = JSON.stringify(data,null,2);

    } catch(error) {

        output.textContent = error.message;

    }

}


async function rebuildAPK() {

    const file = document.getElementById("apkFile").files[0];

    if(!file) return alert("Select APK");

    const form = new FormData();

    form.append("file",file);

    const output = document.getElementById("apkResult");

    output.textContent = "Rebuilding...";

    try {

        const data = await request("/rebuild-apk",{
            method:"POST",
            body:form
        });

        const link = document.createElement("a");

        link.href = data.download_url;

        link.textContent = "Download rebuilt APK";

        output.replaceChildren(link);

    } catch(error) {

        output.textContent = error.message;

    }

}


// DEX ANALYZER

function dexPage() {

    panel("DEX ANALYZER",`

        <input type="file" id="dexFile" accept=".dex">

        <button onclick="analyzeDEX()">ANALYZE DEX</button>

        <pre id="dexResult"></pre>

    `);

}


async function analyzeDEX() {

    const file = document.getElementById("dexFile").files[0];

    if(!file) return alert("Select DEX");

    const form = new FormData();

    form.append("file",file);

    const output = document.getElementById("dexResult");

    output.textContent = "Analyzing...";

    try {

        const data = await request("/analyze-dex",{
            method:"POST",
            body:form
        });

        output.textContent = JSON.stringify(data,null,2);

    } catch(error) {

        output.textContent = error.message;

    }

}


// MEMORY

async function historyPage() {

    panel("FLAXXI MEMORY",`

        <div id="historyResult">Loading...</div>

        <button onclick="clearHistory()">CLEAR HISTORY</button>

    `);

    try {

        const data = await request("/history");

        const output = document.getElementById("historyResult");

        output.replaceChildren();

        data.history.forEach(item=>{

            const div = document.createElement("div");

            div.className = "message";

            div.textContent = item.role + ": " + item.message;

            output.appendChild(div);

        });

    } catch(error) {

        document.getElementById("historyResult").textContent =
            error.message;

    }

}


async function clearHistory() {

    if(!confirm("Delete all chat history?")) return;

    await request("/history",{
        method:"DELETE"
    });

    historyPage();

}


if(getToken()) {

    startApp();

}
