document.addEventListener("DOMContentLoaded", function () {
  const categoryCards = document.querySelectorAll(".category-card");
  const homeContainer = document.querySelector(".home-container");
  const webContainer = document.querySelector(".web-container");
  const mobileContainer = document.querySelector(".mobile-container");
  const cryptoOptions = document.querySelector(".crypto-container");
  const joinUsContainer = document.querySelector(".join-us-container");
  const tentacleTitle = document.querySelector("h1 span.clickable");

  // Hide all content containers initially except home
  webContainer.style.display = "none";
  mobileContainer.style.display = "none";
  cryptoOptions.style.display = "none";
  joinUsContainer.style.display = "none";
  homeContainer.style.display = "block";

  // Add click event for the Tentacle title to return to home
  tentacleTitle.addEventListener("click", function () {
    // Remove active class from all cards
    categoryCards.forEach((c) => c.classList.remove("active"));

    // Hide all content containers
    webContainer.style.display = "none";
    mobileContainer.style.display = "none";
    cryptoOptions.style.display = "none";
    joinUsContainer.style.display = "none";

    // Show home container
    homeContainer.style.display = "block";
  });

  categoryCards.forEach((card) => {
    card.addEventListener("click", function () {
      // Remove active class from all cards
      categoryCards.forEach((c) => c.classList.remove("active"));

      // Add active class to clicked card
      this.classList.add("active");

      // Get category from data attribute
      const category = this.getAttribute("data-category");

      // Hide all content containers first
      homeContainer.style.display = "none";
      webContainer.style.display = "none";
      mobileContainer.style.display = "none";
      cryptoOptions.style.display = "none";
      joinUsContainer.style.display = "none";

      // Show the appropriate container based on category
      if (category === "web") {
        webContainer.style.display = "block";
      } else if (category === "mobile") {
        mobileContainer.style.display = "block";
      } else if (category === "crypto") {
        cryptoOptions.style.display = "block";
      } else if (category === "join") {
        joinUsContainer.style.display = "block";
      } else {
        // Default to showing home container
        homeContainer.style.display = "block";
      }
    });
  });

  // Code for the analyze buttons
  const analyzeButton = document.getElementById("analyzeButton");
  const mobileAnalyzeButton = document.getElementById("mobileAnalyzeButton");
  const modal = document.getElementById("analysisModal");
  const closeButton = document.querySelector(".close-button");
  const analysisOutput = document.getElementById("analysisOutput");

  analyzeButton.addEventListener("click", function () {
    const code = document.getElementById("codeInput").value;
    if (code.trim() === "") {
      alert("Please enter some code to analyze.");
      return;
    }

    // Display modal with loading message
    analysisOutput.textContent = "Analyzing your code...";
    modal.style.display = "block";

    // Simulate analysis (replace with actual API call)
    setTimeout(() => {
      analysisOutput.textContent =
        "Your code has been analyzed. Here are some suggestions for improvement...";
    }, 1500);
  });

  mobileAnalyzeButton.addEventListener("click", function () {
    const code = document.getElementById("mobileCodeInput").value;
    if (code.trim() === "") {
      alert("Please enter some code to analyze.");
      return;
    }

    // Display modal with loading message
    analysisOutput.textContent = "Analyzing your mobile code...";
    modal.style.display = "block";

    // Simulate analysis (replace with actual API call)
    setTimeout(() => {
      analysisOutput.textContent =
        "Your mobile code has been analyzed. Here are some suggestions for improvement...";
    }, 1500);
  });

  closeButton.addEventListener("click", function () {
    modal.style.display = "none";
  });

  window.addEventListener("click", function (event) {
    if (event.target === modal) {
      modal.style.display = "none";
    }
  });

  // Handle copy functionality for crypto addresses
  const copyIcons = document.querySelectorAll(".copy-icon");
  copyIcons.forEach((icon) => {
    icon.addEventListener("click", function () {
      const address = this.parentElement.textContent.trim().slice(0, -1);
      navigator.clipboard
        .writeText(address)
        .then(() => {
          alert("Address copied to clipboard!");
        })
        .catch((err) => {
          console.error("Could not copy text: ", err);
        });
    });
  });

  // Form submission handling with dedicated modal
  const joinForm = document.getElementById("joinUsForm");
  const submissionModal = document.getElementById("submissionModal");
  const submissionOutput = document.getElementById("submissionOutput");
  const closeSubmissionButton = document.querySelector(
    ".submission-close-button"
  );

  if (joinForm) {
    joinForm.addEventListener("submit", function (e) {
      e.preventDefault();

      // Display submission modal with thank you message directly
      submissionOutput.textContent =
        "Thank you for your interest! We will contact you soon.";
      submissionModal.style.display = "block";

      // Reset the form
      joinForm.reset();
    });
  }

  // Close button for submission modal
  if (closeSubmissionButton) {
    closeSubmissionButton.addEventListener("click", function () {
      submissionModal.style.display = "none";
    });
  }

  // Close submission modal when clicking outside
  window.addEventListener("click", function (event) {
    if (event.target === submissionModal) {
      submissionModal.style.display = "none";
    }
  });
});

// Platform selector functionality for web
const codePlatformOptions = document.querySelectorAll(".code-platform-option");
codePlatformOptions.forEach((option) => {
  option.addEventListener("click", function () {
    // Remove active class from all options
    codePlatformOptions.forEach((opt) => opt.classList.remove("active"));
    // Add active class to clicked option
    this.classList.add("active");

    // You can add logic here to change placeholder or other elements based on selected platform
    const platform = this.getAttribute("data-platform");
    const codeInput = document.getElementById("codeInput");

    if (platform === "javascript") {
      codeInput.placeholder = "Enter JavaScript code...";
    } else if (platform === "python") {
      codeInput.placeholder = "Enter Python code...";
    } else if (platform === "php") {
      codeInput.placeholder = "Enter PHP code...";
    }
  });
});

// Platform selector functionality for mobile
const mobilePlatformOptions = document.querySelectorAll(
  ".mobile-platform-option"
);
mobilePlatformOptions.forEach((option) => {
  option.addEventListener("click", function () {
    // Remove active class from all options
    mobilePlatformOptions.forEach((opt) => opt.classList.remove("active"));
    // Add active class to clicked option
    this.classList.add("active");

    // You can add logic here to change placeholder or other elements based on selected platform
    const platform = this.getAttribute("data-platform");
    const mobileCodeInput = document.getElementById("mobileCodeInput");

    if (platform === "android") {
      mobileCodeInput.placeholder = "Enter Android code...";
    } else if (platform === "ios") {
      mobileCodeInput.placeholder = "Enter iOS code...";
    }
  });
});

// Consistent container heights
const sections = [
  document.querySelector(".home-container"),
  document.querySelector(".web-container"),
  document.querySelector(".mobile-container"),
  document.querySelector(".crypto-container"),
  document.querySelector(".join-us-container"),
];

sections.forEach((section) => {
  if (section) {
    section.style.minHeight = "350px";
  }
});
