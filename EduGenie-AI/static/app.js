const task =
    document.getElementById("task");

const fields =
    document.getElementById(
        "dynamic-fields"
    );

const submitBtn =
    document.getElementById(
        "submit-btn"
    );

const buttonText =
    document.getElementById(
        "button-text"
    );

const spinner =
    document.getElementById(
        "spinner"
    );

const clearBtn =
    document.getElementById(
        "clear-btn"
    );

const result =
    document.getElementById(
        "result"
    );

const status =
    document.getElementById(
        "status"
    );


// =====================================================
// TASK CONFIGURATION
// =====================================================

const configs = {

    qa: {

        button: "Ask EduGenie",

        html: `

            <label
                class="field-label"
                for="main-input"
            >
                Your Question
            </label>

            <textarea
                id="main-input"
                placeholder="Example: What is the difference between TCP and UDP?"
            ></textarea>

        `
    },


    explain: {

        button: "Explain Topic",

        html: `

            <label
                class="field-label"
                for="main-input"
            >
                Topic
            </label>

            <textarea
                id="main-input"
                placeholder="Example: Explain the OSI model for a beginner."
            ></textarea>

        `
    },


    summarize: {

        button: "Summarize",

        html: `

            <label
                class="field-label"
                for="main-input"
            >
                Text to Summarize
            </label>

            <textarea
                id="main-input"
                placeholder="Paste your notes or educational passage here..."
            ></textarea>

        `
    },


    quiz: {

        button: "Generate Quiz",

        html: `

            <label
                class="field-label"
                for="main-input"
            >
                Topic or Passage
            </label>

            <textarea
                id="main-input"
                placeholder="Paste your notes or passage..."
            ></textarea>


            <label
                class="field-label"
                for="count"
            >
                Number of Questions
            </label>


            <select id="count">

                <option value="3">
                    3 Questions
                </option>

                <option value="5">
                    5 Questions
                </option>

                <option value="10">
                    10 Questions
                </option>

            </select>

        `
    },


    learn: {

        button: "Build Learning Path",

        html: `

            <label
                class="field-label"
                for="topic"
            >
                Topic
            </label>

            <input
                id="topic"
                placeholder="Example: SQL"
            >


            <label
                class="field-label"
                for="level"
            >
                Current Level
            </label>


            <select id="level">

                <option value="beginner">
                    Beginner
                </option>

                <option value="intermediate">
                    Intermediate
                </option>

                <option value="advanced">
                    Advanced
                </option>

            </select>


            <label
                class="field-label"
                for="goals"
            >
                Learning Goal
            </label>


            <textarea
                id="goals"
                placeholder="Example: Prepare for placements and build two projects."
            ></textarea>

        `
    }

};


// =====================================================
// RENDER INPUT FIELDS
// =====================================================

function renderFields() {

    const config =
        configs[
            task.value
        ];

    fields.innerHTML =
        config.html;

    buttonText.textContent =
        config.button;
}


renderFields();


// =====================================================
// LOADING
// =====================================================

function setLoading(
    loading
) {

    submitBtn.disabled =
        loading;

    spinner.classList.toggle(
        "hidden",
        !loading
    );


    buttonText.textContent =
        loading
            ? "Working..."
            : configs[
                task.value
            ].button;


    status.textContent =
        loading
            ? "Generating"
            : "Ready";

    status.classList.remove(
        "error"
    );
}


// =====================================================
// ERROR
// =====================================================

function setError(
    message
) {

    result.classList.remove(
        "empty"
    );

    result.textContent =
        message;

    status.textContent =
        "Error";

    status.classList.add(
        "error"
    );
}


// =====================================================
// TEXT RESULT
// =====================================================

function renderText(
    text
) {

    result.classList.remove(
        "empty"
    );

    result.textContent =
        text;
}


// =====================================================
// QUIZ RESULT
// =====================================================

function renderQuiz(
    quiz
) {

    result.classList.remove(
        "empty"
    );


    let score = 0;

    let answered = 0;


    const scoreBox =
        document.createElement(
            "div"
        );

    scoreBox.className =
        "quiz-score";


    scoreBox.textContent =
        `Score: 0 / ${quiz.questions.length}`;


    result.innerHTML =
        "";


    result.appendChild(
        scoreBox
    );


    quiz.questions.forEach(
        (question, index) => {

            const box =
                document.createElement(
                    "div"
                );

            box.className =
                "quiz-question";


            const title =
                document.createElement(
                    "h3"
                );


            title.textContent =
                `${index + 1}. ${question.question}`;


            box.appendChild(
                title
            );


            question.options.forEach(
                option => {

                    const button =
                        document.createElement(
                            "button"
                        );


                    button.className =
                        "quiz-option";


                    button.textContent =
                        option;


                    button.addEventListener(
                        "click",
                        () => {

                            if (
                                box.dataset.answered ===
                                "true"
                            ) {

                                return;

                            }


                            box.dataset.answered =
                                "true";


                            answered++;


                            const buttons =
                                box.querySelectorAll(
                                    ".quiz-option"
                                );


                            buttons.forEach(
                                buttonElement => {

                                    buttonElement.disabled =
                                        true;


                                    if (
                                        buttonElement.textContent ===
                                        question.correct_answer
                                    ) {

                                        buttonElement.classList.add(
                                            "correct"
                                        );

                                    }

                                }
                            );


                            if (
                                option ===
                                question.correct_answer
                            ) {

                                score++;

                            }
                            else {

                                button.classList.add(
                                    "wrong"
                                );

                            }


                            explanation.style.display =
                                "block";


                            scoreBox.textContent =
                                `Score: ${score} / ${quiz.questions.length}`;


                            if (
                                answered ===
                                quiz.questions.length
                            ) {

                                status.textContent =
                                    `Completed: ${score}/${quiz.questions.length}`;

                            }

                        }
                    );


                    box.appendChild(
                        button
                    );

                }
            );


            const explanation =
                document.createElement(
                    "div"
                );


            explanation.className =
                "quiz-explanation";


            explanation.textContent =
                `Explanation: ${question.explanation}`;


            box.appendChild(
                explanation
            );


            result.appendChild(
                box
            );

        }
    );
}


// =====================================================
// RUN TASK
// =====================================================

async function runTask() {

    setLoading(
        true
    );


    try {

        let endpoint;

        let payload;


        // ------------------------------
        // Q&A
        // ------------------------------

        if (
            task.value === "qa"
        ) {

            const question =
                document
                    .getElementById(
                        "main-input"
                    )
                    .value
                    .trim();


            if (!question) {

                throw new Error(
                    "Please enter a question."
                );

            }


            endpoint =
                "/qa";


            payload = {

                question:
                    question

            };

        }


        // ------------------------------
        // EXPLAIN
        // ------------------------------

        if (
            task.value === "explain"
        ) {

            const text =
                document
                    .getElementById(
                        "main-input"
                    )
                    .value
                    .trim();


            if (!text) {

                throw new Error(
                    "Please enter a topic."
                );

            }


            endpoint =
                "/explain";


            payload = {

                text:
                    text

            };

        }


        // ------------------------------
        // SUMMARY
        // ------------------------------

        if (
            task.value === "summarize"
        ) {

            const text =
                document
                    .getElementById(
                        "main-input"
                    )
                    .value
                    .trim();


            if (!text) {

                throw new Error(
                    "Please enter text to summarize."
                );

            }


            endpoint =
                "/summarize";


            payload = {

                text:
                    text

            };

        }


        // ------------------------------
        // QUIZ
        // ------------------------------

        if (
            task.value === "quiz"
        ) {

            const text =
                document
                    .getElementById(
                        "main-input"
                    )
                    .value
                    .trim();


            if (!text) {

                throw new Error(
                    "Please enter a topic or passage."
                );

            }


            endpoint =
                "/quiz";


            payload = {

                text:
                    text,

                count:
                    Number(
                        document
                            .getElementById(
                                "count"
                            )
                            .value
                    )

            };

        }


        // ------------------------------
        // LEARNING PATH
        // ------------------------------

        if (
            task.value === "learn"
        ) {

            const topic =
                document
                    .getElementById(
                        "topic"
                    )
                    .value
                    .trim();


            const level =
                document
                    .getElementById(
                        "level"
                    )
                    .value;


            const goals =
                document
                    .getElementById(
                        "goals"
                    )
                    .value
                    .trim();


            if (!topic) {

                throw new Error(
                    "Please enter a learning topic."
                );

            }


            endpoint =
                "/learn/recommendations";


            payload = {

                topic:
                    topic,

                level:
                    level,

                goals:
                    goals

            };

        }


        // =================================================
        // API REQUEST
        // =================================================

        const response =
            await fetch(
                endpoint,
                {

                    method:
                        "POST",

                    headers: {

                        "Content-Type":
                            "application/json"

                    },

                    body:
                        JSON.stringify(
                            payload
                        )

                }
            );


        const data =
            await response.json();


        if (!response.ok) {

            throw new Error(
                data.detail ||
                "The server returned an error."
            );

        }


        status.textContent =
            "Completed";


        status.classList.remove(
            "error"
        );


        // =================================================
        // DISPLAY RESULT
        // =================================================

        if (
            task.value === "quiz"
        ) {

            renderQuiz(
                data.quiz
            );

        }
        else if (

            task.value === "qa" ||
            task.value === "explain" ||
            task.value === "summarize"

        ) {

            renderText(
                data.answer ||
                data.summary ||
                ""
            );

        }
        else {

            renderText(
                data.recommendations ||
                ""
            );

        }

    }
    catch (error) {

        setError(
            error.message
        );

    }
    finally {

        submitBtn.disabled =
            false;

        spinner.classList.add(
            "hidden"
        );

        buttonText.textContent =
            configs[
                task.value
            ].button;

    }

}


// =====================================================
// EVENTS
// =====================================================

task.addEventListener(
    "change",
    renderFields
);


submitBtn.addEventListener(
    "click",
    runTask
);


clearBtn.addEventListener(
    "click",
    () => {

        renderFields();


        result.className =
            "result empty";


        result.textContent =
            "Your AI-generated learning result will appear here.";


        status.textContent =
            "Ready";


        status.classList.remove(
            "error"
        );

    }
);