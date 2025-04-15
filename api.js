document.getElementById("enhanceButton").addEventListener("click", async () => {
  const codeInput = document.getElementById("codeInput").value;
  const enhancedCodeElement = document.getElementById("enhancedCode");

  const apiKey = "api-key";
  const apiUrl = "URL_ADDRESS.openai.com/v1/chat/completions";

  try {
    const response = await fetch(apiUrl, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${apiKey}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        model: "gpt-4-turbo-preview",
        messages: [
          {
            role: "user",
            content: `Optimize and refactor this code:\n\`\`\`\n${codeInput}\n\`\`\``,
          },
        ],
      }),
    });

    if (!response.ok) {
      throw new Error("API request failed");
    }

    const data = await response.json();
    enhancedCodeElement.textContent =
      data.choices[0]?.message?.content || "No output";
  } catch (error) {
    console.error("Error:", error);
    enhancedCodeElement.textContent = "Error enhancing code. Check console.";
  }
});
