// background.js
const grabBtn = document.getElementById("grabBtn");
grabBtn.addEventListener("click",() => {    
    chrome.tabs.query({ currentWindow: true }, async function (tabs) {
        try {
            const res = await fetch('http://127.0.0.1:5000', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({'tabs': tabs}),
                mode: "no-cors"
            });

            if (res.ok) {
                console.log('Send success!');
            } else {
                throw new Error(`Send error, ${res.statusText}, with status ${res.status}, ${res.ok}`);
            } 
        } catch (error) {
            console.error('Error', error);
        }
    });
})