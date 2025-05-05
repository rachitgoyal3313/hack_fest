document.addEventListener("DOMContentLoaded", () => {
  // Get all form elements
  const textForm = document.getElementById("textForm");
  const textResult = document.getElementById("textResult");
  const textAlert = document.getElementById("textAlert");
  const textPrediction = document.getElementById("textPrediction");
  const textConfidence = document.getElementById("textConfidence");
  const textProgressBar = document.getElementById("textProgressBar");

  // Verify all required elements exist
  if (!textForm || !textResult || !textAlert || !textPrediction || !textConfidence || !textProgressBar) {
    console.error("Required text detection elements not found!");
    return;
  }

  // Text Form Submission
  textForm.addEventListener("submit", function (e) {
    e.preventDefault();
    
    const formData = new FormData(this);

    // Show processing
    showProcessing("text");

    fetch("/detect/text", {
      method: "POST",
      body: formData,
    })
      .then((response) => {
        if (response.status === 503) {
          // Model is loading, retry after 3 seconds
          showProcessing("text", true);
          return response.json().then(data => {
            setTimeout(() => {
              this.dispatchEvent(new Event('submit'));
            }, 3000);
            throw new Error(data.error || 'Model is loading, retrying...');
          });
        }
        if (!response.ok) {
          return response.json().then(data => {
            throw new Error(data.error || 'An error occurred during processing.');
          });
        }
        return response.json();
      })
      .then((data) => {
        if (!data) {
          throw new Error('No data received from server');
        }
        displayTextResult(data);
      })
      .catch((error) => {
        console.error("Error:", error);
        displayError("text", error.message);
      });
  });

  // Audio Form Submission
  const audioForm = document.getElementById("audioForm");
  const audioResult = document.getElementById("audioResult");
  const audioAlert = document.getElementById("audioAlert");
  const audioPrediction = document.getElementById("audioPrediction");
  const audioConfidence = document.getElementById("audioConfidence");
  const audioProgressBar = document.getElementById("audioProgressBar");

  if (!audioForm || !audioResult || !audioAlert || !audioPrediction || !audioConfidence || !audioProgressBar) {
    console.error("Required audio detection elements not found!");
    return;
  }

  audioForm.addEventListener("submit", function (e) {
    e.preventDefault();
    
    const formData = new FormData(this);

    // Show processing
    showProcessing("audio");

    fetch("/detect/audio", {
      method: "POST",
      body: formData,
    })
      .then((response) => response.json())
      .then((data) => {
        if (!data) {
          throw new Error('No data received from server');
        }
        displayAudioResult(data);
      })
      .catch((error) => {
        console.error("Error:", error);
        displayError("audio", error.message || "An error occurred during processing.");
      });
  });

  // Image Form Submission
  const imageForm = document.getElementById("imageForm");
  const imageResult = document.getElementById("imageResult");
  const imageAlert = document.getElementById("imageAlert");
  const imagePrediction = document.getElementById("imagePrediction");
  const imageConfidence = document.getElementById("imageConfidence");
  const imageProgressBar = document.getElementById("imageProgressBar");
  const imageFile = document.getElementById("imageFile");
  const imagePreview = document.getElementById("imagePreview");

  if (!imageForm || !imageResult || !imageAlert || !imagePrediction || !imageConfidence || !imageProgressBar || !imageFile || !imagePreview) {
    console.error("Required image detection elements not found!");
    return;
  }

  imageForm.addEventListener("submit", function (e) {
    e.preventDefault();
    
    const formData = new FormData(this);

    // Show processing
    showProcessing("image");

    // Preview image
    const imageFileInput = imageFile.files[0];
    if (imageFileInput) {
      const reader = new FileReader();
      reader.onload = (e) => {
        imagePreview.src = e.target.result;
      };
      reader.readAsDataURL(imageFileInput);
    }

    fetch("/detect/image", {
      method: "POST",
      body: formData,
    })
      .then((response) => response.json())
      .then((data) => {
        if (!data) {
          throw new Error('No data received from server');
        }
        displayImageResult(data);
      })
      .catch((error) => {
        console.error("Error:", error);
        displayError("image", error.message || "An error occurred during processing.");
      });
  });

  // Video Form Submission
  const videoForm = document.getElementById("videoForm");
  const videoResult = document.getElementById("videoResult");
  const videoAlert = document.getElementById("videoAlert");
  const videoPrediction = document.getElementById("videoPrediction");
  const videoConfidence = document.getElementById("videoConfidence");
  const videoFramesAnalyzed = document.getElementById("videoFramesAnalyzed");
  const videoFakeFrames = document.getElementById("videoFakeFrames");
  const videoFakePercentage = document.getElementById("videoFakePercentage");
  const videoProgressBar = document.getElementById("videoProgressBar");

  if (!videoForm || !videoResult || !videoAlert || !videoPrediction || !videoConfidence || !videoFramesAnalyzed || !videoFakeFrames || !videoFakePercentage || !videoProgressBar) {
    console.error("Required video detection elements not found!");
    return;
  }

  videoForm.addEventListener("submit", function (e) {
    e.preventDefault();
    
    const formData = new FormData(this);

    // Show processing
    showProcessing("video");

    fetch("/detect/video", {
      method: "POST",
      body: formData,
    })
      .then((response) => response.json())
      .then((data) => {
        if (!data) {
          throw new Error('No data received from server');
        }
        displayVideoResult(data);
      })
      .catch((error) => {
        console.error("Error:", error);
        displayError("video", error.message || "An error occurred during processing.");
      });
  });

  // Helper Functions
  function showProcessing(type, isLoading = false) {
    const resultDiv = document.getElementById(`${type}Result`);
    if (!resultDiv) return;
    
    resultDiv.classList.remove("d-none");

    const alertDiv = document.getElementById(`${type}Alert`);
    if (alertDiv) {
      alertDiv.className = isLoading ? "alert alert-loading" : "alert alert-processing";
      const message = isLoading ? 'Loading model, please wait...' : 'Processing...';
      alertDiv.innerHTML = `<div class="spinner-border spinner-border-sm" role="status"></div> ${message}`;
    }

    const progressBar = document.getElementById(`${type}ProgressBar`);
    if (progressBar) {
      progressBar.style.width = "100%";
      progressBar.className = "progress-bar progress-bar-striped progress-bar-animated";
    }
  }

  function displayTextResult(data) {
    const resultDiv = document.getElementById("textResult");
    const alertDiv = document.getElementById("textAlert");
    const predictionSpan = document.getElementById("textPrediction");
    const confidenceSpan = document.getElementById("textConfidence");
    const progressBar = document.getElementById("textProgressBar");

    if (!resultDiv || !alertDiv || !predictionSpan || !confidenceSpan || !progressBar) {
      console.error("Required result elements not found!");
      return;
    }

    if (data.error) {
      displayError("text", data.error);
      return;
    }

    predictionSpan.textContent = data.prediction || '';
    confidenceSpan.textContent = data.confidence || '';

    if (data.is_ai_generated) {
      alertDiv.className = "alert alert-danger";
      progressBar.className = "progress-bar bg-danger";
    } else {
      alertDiv.className = "alert alert-success";
      progressBar.className = "progress-bar bg-success";
    }

    progressBar.style.width = `${data.confidence || 0}%`;
  }

  function displayAudioResult(data) {
    const resultDiv = document.getElementById("audioResult");
    const alertDiv = document.getElementById("audioAlert");
    const predictionSpan = document.getElementById("audioPrediction");
    const confidenceSpan = document.getElementById("audioConfidence");
    const progressBar = document.getElementById("audioProgressBar");

    if (!resultDiv || !alertDiv || !predictionSpan || !confidenceSpan || !progressBar) {
      console.error("Required result elements not found!");
      return;
    }

    if (data.error) {
      displayError("audio", data.error);
      return;
    }

    predictionSpan.textContent = data.prediction || '';
    confidenceSpan.textContent = data.confidence || '';

    if (data.is_spoofed) {
      alertDiv.className = "alert alert-danger";
      progressBar.className = "progress-bar bg-danger";
    } else {
      alertDiv.className = "alert alert-success";
      progressBar.className = "progress-bar bg-success";
    }

    progressBar.style.width = `${data.confidence || 0}%`;
  }

  function displayImageResult(data) {
    const resultDiv = document.getElementById("imageResult");
    const alertDiv = document.getElementById("imageAlert");
    const predictionSpan = document.getElementById("imagePrediction");
    const confidenceSpan = document.getElementById("imageConfidence");
    const progressBar = document.getElementById("imageProgressBar");

    if (!resultDiv || !alertDiv || !predictionSpan || !confidenceSpan || !progressBar) {
      console.error("Required result elements not found!");
      return;
    }

    if (data.error) {
      displayError("image", data.error);
      return;
    }

    predictionSpan.textContent = data.prediction || '';
    confidenceSpan.textContent = data.confidence || '';

    if (data.is_fake) {
      alertDiv.className = "alert alert-danger";
      progressBar.className = "progress-bar bg-danger";
    } else {
      alertDiv.className = "alert alert-success";
      progressBar.className = "progress-bar bg-success";
    }

    progressBar.style.width = `${data.confidence || 0}%`;
  }

  function displayVideoResult(data) {
    const resultDiv = document.getElementById("videoResult");
    const alertDiv = document.getElementById("videoAlert");
    const predictionSpan = document.getElementById("videoPrediction");
    const confidenceSpan = document.getElementById("videoConfidence");
    const framesSpan = document.getElementById("videoFramesAnalyzed");
    const fakeFramesSpan = document.getElementById("videoFakeFrames");
    const fakePercentageSpan = document.getElementById("videoFakePercentage");
    const progressBar = document.getElementById("videoProgressBar");

    if (!resultDiv || !alertDiv || !predictionSpan || !confidenceSpan || !framesSpan || !fakeFramesSpan || !fakePercentageSpan || !progressBar) {
      console.error("Required result elements not found!");
      return;
    }

    if (data.error) {
      displayError("video", data.error);
      return;
    }

    predictionSpan.textContent = data.prediction || '';
    confidenceSpan.textContent = data.confidence || '';
    framesSpan.textContent = data.frames_analyzed || '';
    fakeFramesSpan.textContent = data.fake_frames || '';
    fakePercentageSpan.textContent = data.fake_percentage || '';

    if (data.is_fake) {
      alertDiv.className = "alert alert-danger";
      progressBar.className = "progress-bar bg-danger";
    } else {
      alertDiv.className = "alert alert-success";
      progressBar.className = "progress-bar bg-success";
    }

    progressBar.style.width = `${data.confidence || 0}%`;
  }

  function displayError(type, message) {
    const alertDiv = document.getElementById(`${type}Alert`);
    if (!alertDiv) return;
    
    alertDiv.className = "alert alert-warning";
    alertDiv.innerHTML = `<strong>Error:</strong> ${message}`;

    const progressBar = document.getElementById(`${type}ProgressBar`);
    if (progressBar) {
      progressBar.style.width = "100%";
      progressBar.className = "progress-bar bg-warning";
    }
  }
});
