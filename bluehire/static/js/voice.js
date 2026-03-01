// Simple multilingual & voice-assist helper using browser APIs

const messages = {
  en: {
    help: "Welcome to BlueHire. Use the big buttons to find jobs or post jobs. Scroll down to see job cards.",
  },
  hi: {
    help: "ब्लू हायर में आपका स्वागत है। बड़े बटन से नौकरी खोजें या नौकरी पोस्ट करें। नीचे स्क्रोल करके काम की जानकारी देखें।",
  },
};

let currentLang = "en";

function setLanguage(lang) {
  currentLang = messages[lang] ? lang : "en";
}

function speakHelp() {
  if (!("speechSynthesis" in window)) {
    alert("Voice help is not supported in this browser.");
    return;
  }
  const text = messages[currentLang].help;
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = currentLang === "hi" ? "hi-IN" : "en-IN";
  window.speechSynthesis.cancel();
  window.speechSynthesis.speak(utterance);
}


