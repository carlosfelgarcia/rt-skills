// Shared quiz widget for lessons. render.py inlines it and puts the questions in #quiz-data.
// Question, answer and feedback strings are HTML that render.py has already escaped.
(function () {
  var data = JSON.parse(document.getElementById("quiz-data").textContent);
  var root = document.getElementById("quiz");
  var answered = 0;
  var missed = [];

  data.questions.forEach(function (q, qi) {
    var box = document.createElement("div");
    box.className = "question";
    var text = document.createElement("p");
    text.className = "q";
    text.innerHTML = (qi + 1) + ". " + q.text;
    var options = document.createElement("div");
    options.className = "options";
    var feedback = document.createElement("p");
    feedback.className = "feedback";
    feedback.hidden = true;

    q.options.forEach(function (option, oi) {
      var button = document.createElement("button");
      button.type = "button";
      button.innerHTML = option;
      button.addEventListener("click", function () {
        var right = oi === q.answer;
        if (!right) missed.push("Q" + (qi + 1));
        options.querySelectorAll("button").forEach(function (b, bi) {
          b.disabled = true;
          if (bi === q.answer) b.classList.add("right");
        });
        if (!right) button.classList.add("wrong");
        feedback.hidden = false;
        feedback.innerHTML = (right ? "Right. " : "Not quite. ") + q.feedback;
        answered += 1;
        if (answered === data.questions.length) finish();
      });
      options.appendChild(button);
    });

    box.appendChild(text);
    box.appendChild(options);
    box.appendChild(feedback);
    root.appendChild(box);
  });

  // The agent cannot see this page, so the result line is how it learns what stuck.
  function finish() {
    var total = data.questions.length;
    var line = data.id + ": " + (total - missed.length) + "/" + total +
      (missed.length ? ", missed " + missed.join(", ") : "");
    var result = document.createElement("div");
    result.className = "result";
    result.innerHTML = "Paste this line in the chat where you ran the review: <code></code>";
    result.querySelector("code").textContent = line;
    var copy = document.createElement("button");
    copy.type = "button";
    copy.textContent = "Copy";
    copy.addEventListener("click", function () {
      if (navigator.clipboard) navigator.clipboard.writeText(line).then(function () { copy.textContent = "Copied"; });
    });
    result.appendChild(copy);
    root.appendChild(result);
  }
})();
