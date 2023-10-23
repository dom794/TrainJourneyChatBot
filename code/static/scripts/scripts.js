const userInputForm = document.querySelector(".user-input-form");
const userInput = document.querySelector(".user-input");
const chatArea = document.querySelector(".chat-area");
userInputForm.addEventListener("submit", (event) => {
  event.preventDefault();
  const msgText = userInput.value;
  if (!msgText) return;
  appendMessage("You", "right", msgText);
  userInput.value = "";
  botResponse(msgText);
});
function appendMessage(name, side, text) {
  const time = setDateFormat(new Date());
  const msgHTML = `
    <div class="msg ${side}-msg">
        <div class="msg-bubble">
        <div class="msg-info">
            <div class="msg-info-name">${name}</div>
            <div class="msg-info-time">${time}</div>
        </div>
        <div class="msg-text">${text}</div>
        </div>
    </div>
    `;
  chatArea.insertAdjacentHTML("beforeend", msgHTML);
  chatArea.scrollTop += 500;
}

function botResponse(rawText) {
  // Bot Response
  $.get("/get", { msg: rawText }).done(function (data) {
    console.log(rawText);
    console.log(data);
    const msgText = data;
    appendMessage("Thomas 🚂", "left", msgText);
  });
}

function setDateFormat(date) {
  let hours = date.getHours();
  let minutes = date.getMinutes();
  let ampm = hours >= 12 ? "pm" : "am";
  hours = hours % 12;
  hours = hours ? hours : 12; // the hour '0' should be '12'
  minutes = minutes < 10 ? "0" + minutes : minutes;
  let strTime = hours + ":" + minutes + " " + ampm;
  return strTime;
}

function enableSpeech() {
  fetch("/enable_speech", { method: "POST" })
    .then((response) => {
      if (!response.ok) {
        throw new Error("Error: " + response.statusText);
      }
    })
    .catch((error) => console.log("Error: " + error));
}

// attach the toggleTTS function to the button click event
const tts = document.querySelector("#tts-button");
tts.addEventListener("click", enableSpeech);
