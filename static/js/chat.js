document.addEventListener("DOMContentLoaded", () => {
    const app = document.getElementById("chat-app");
    const form = document.getElementById("chat-form");
    const input = document.getElementById("chat-input");
    const submitButton = document.getElementById("chat-submit");
    const messages = document.getElementById("chat-messages");
    const suggestionButtons = document.querySelectorAll(".chat-suggestion");
    const suggestions = document.querySelector(".chat-suggestions");

    if (!app || !form || !input || !submitButton || !messages) {
        return;
    }

    const language = app.dataset.language || "pl";

    const conversationHistory = [];
    const maxHistoryMessages = 4;

    for (const button of suggestionButtons) {
        button.addEventListener(
            "click",
            () => {
                const question =
                    language === "pl"
                        ? button.dataset.questionPl
                        : button.dataset.questionEn;

                if (!question) {
                    return;
                }

                input.value = question;
                resizeInput();
                input.focus();
            }
        );
    }

    form.addEventListener("submit", async (event) => {
        event.preventDefault();

        const message = input.value.trim();

        if (!message) {
            return;
        }

        hideSuggestions();
        addMessage("user", message);

        input.value = "";
        resizeInput();
        setLoading(true);

        const loadingMessage = addLoadingMessage();

        try {
            const response = await fetch(
                "/api/chat/stream",
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({
                        message,
                        language,
                        history: conversationHistory,
                    }),
                }
            );

            if (!response.ok) {
                throw new Error(
                    `HTTP ${response.status}`
                );
            }

            const data = await readChatStream(
                response,
                (stage) => {
                    if (stage === "processing") {
                        loadingMessage.textContent =
                            language === "pl"
                                ? "Analizuję źródła..."
                                : "Analyzing sources...";
                    }
                }
            );

            loadingMessage.remove();

            addAssistantResponse(data);

            conversationHistory.push(
                {
                    role: "user",
                    content: message,
                },
                {
                    role: "assistant",
                    content: data.answer,
                }
            );

            if (
                conversationHistory.length
                > maxHistoryMessages
            ) {
                conversationHistory.splice(
                    0,
                    conversationHistory.length
                        - maxHistoryMessages
                );
            }
        } catch (error) {
            console.error("Chat request failed:", error);

            loadingMessage.remove();

            addMessage(
                "assistant",
                language === "pl"
                    ? "Nie udało się teraz uzyskać odpowiedzi. Spróbuj ponownie za chwilę."
                    : "The assistant is temporarily unavailable. Please try again shortly.",
                true
            );
        } finally {
            setLoading(false);
            input.focus();
        }
    });

    function addMessage(role, text, isError = false) {
        const row = document.createElement("div");

        row.classList.add(
            "chat-row",
            `chat-row-${role}`
        );

        if (role === "assistant") {
            const avatar = document.createElement("div");

            avatar.classList.add("chat-avatar");
            avatar.textContent = "AI";
            avatar.setAttribute("aria-hidden", "true");

            row.appendChild(avatar);
        }

        const message = document.createElement("div");

        message.classList.add(
            "chat-message",
            `chat-message-${role}`
        );

        if (isError) {
            message.classList.add(
                "chat-message-error"
            );
        }

        message.textContent = text;

        row.appendChild(message);
        messages.appendChild(row);

        scrollToBottom();

        return row;
    }

    function addAssistantResponse(data) {
        const row = document.createElement("div");

        row.classList.add(
            "chat-row",
            "chat-row-assistant"
        );

        const avatar = document.createElement("div");

        avatar.classList.add("chat-avatar");
        avatar.textContent = "AI";
        avatar.setAttribute(
            "aria-hidden",
            "true"
        );

        const wrapper = document.createElement("div");

        wrapper.classList.add(
            "chat-message",
            "chat-message-assistant"
        );

        const answer = document.createElement("div");

        answer.classList.add("chat-answer");

        appendAnswerWithCitations(
            answer,
            data.answer,
            data.sources
        );

        wrapper.appendChild(answer);

        if (data.sources.length > 0) {
            wrapper.appendChild(
                createSources(data.sources)
            );
        }

        row.appendChild(avatar);
        row.appendChild(wrapper);

        messages.appendChild(row);

        scrollToBottom();
    }

    function createSources(sources) {
        const container = document.createElement("details");
        container.classList.add("chat-sources");

        const title = document.createElement("strong");
        const summary = document.createElement("summary");

        summary.textContent = language === "pl" ? `Źródła (${sources.length})` : `Sources (${sources.length})`;

        title.textContent =
            language === "pl"
                ? "Źródła:"
                : "Sources:";

        container.appendChild(summary);

        const list = document.createElement("ul");

        for (const source of sources) {
            const item = document.createElement("li");
            const link = document.createElement("a");

            link.href = buildLocalizedSourceUrl(
                source.source_path
            );

            let label =
                `[${source.number}] ${source.title} — ${source.section}`;

            if (source.subsection) {
                label += ` > ${source.subsection}`;
            }

            link.textContent = label;

            item.appendChild(link);
            list.appendChild(item);
        }

        container.appendChild(list);

        return container;
    }

    function setLoading(isLoading) {
        input.disabled = isLoading;
        submitButton.disabled = isLoading;
    }

    function scrollToBottom() {
        messages.scrollTop = messages.scrollHeight;
    }

    function buildLocalizedSourceUrl(sourcePath) {
        const url = new URL(
            sourcePath,
            window.location.origin
        );

        url.searchParams.set(
            "lang",
            language
        );

        return (
            url.pathname
            + url.search
            + url.hash
        );
    }

    input.addEventListener("keydown", (event) => {
        if (
            event.key === "Enter"
            && !event.shiftKey
            && !event.isComposing
        ) {
            event.preventDefault();

            if (!submitButton.disabled) {
                form.requestSubmit();
            }
        }
    });

    function appendAnswerWithCitations(
        container,
        text,
        sources
    ) {
        const sourceMap = new Map(
            sources.map((source) => [
                source.number,
                source,
            ])
        );

        const citationPattern = /\[(\d+)\]/g;

        let lastIndex = 0;
        let match;

        while (
            (match = citationPattern.exec(text))
            !== null
        ) {
            const textBeforeCitation = text.slice(
                lastIndex,
                match.index
            );

            if (textBeforeCitation) {
                container.appendChild(
                    document.createTextNode(
                        textBeforeCitation
                    )
                );
            }

            const citationNumber = Number(
                match[1]
            );

            const source = sourceMap.get(
                citationNumber
            );

            if (source) {
                const link = document.createElement(
                    "a"
                );

                link.classList.add(
                    "chat-citation"
                );

                link.href =
                    buildLocalizedSourceUrl(
                        source.source_path
                    );

                link.textContent =
                    `[${citationNumber}]`;

                link.title =
                    `${source.title} — ${source.section}`;

                container.appendChild(link);
            } else {
                container.appendChild(
                    document.createTextNode(
                        match[0]
                    )
                );
            }

            lastIndex =
                citationPattern.lastIndex;
        }

        const remainingText = text.slice(
            lastIndex
        );

        if (remainingText) {
            container.appendChild(
                document.createTextNode(
                    remainingText
                )
            );
        }
    }

    async function readChatStream(
        response,
        onStatus
    ) {
        if (!response.body) {
            throw new Error(
                "Streaming response body is unavailable"
            );
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();

        let buffer = "";
        let result = null;
        let streamError = null;

        while (true) {
            const {
                value,
                done,
            } = await reader.read();

            if (value) {
                buffer += decoder.decode(
                    value,
                    {
                        stream: !done,
                    }
                );

                buffer = buffer.replace(
                    /\r\n/g,
                    "\n"
                );
            }

            let separatorIndex;

            while (
                (
                    separatorIndex =
                        buffer.indexOf("\n\n")
                ) !== -1
            ) {
                const block = buffer.slice(
                    0,
                    separatorIndex
                );

                buffer = buffer.slice(
                    separatorIndex + 2
                );

                const event = parseSseBlock(
                    block
                );

                if (!event) {
                    continue;
                }

                if (event.type === "status") {
                    onStatus?.(
                        event.data.stage
                    );
                }

                if (event.type === "result") {
                    result = event.data;
                }

                if (event.type === "error") {
                    streamError =
                        event.data.detail
                        || "Streaming request failed";
                }
            }

            if (done) {
                break;
            }
        }

        if (streamError) {
            throw new Error(streamError);
        }

        if (!result) {
            throw new Error(
                "Stream ended without a result"
            );
        }

        return result;
    }

    function parseSseBlock(block) {
        if (!block.trim()) {
            return null;
        }

        const lines = block.split("\n");

        let type = "message";
        const dataLines = [];

        for (const line of lines) {
            if (line.startsWith("event:")) {
                type = line
                    .slice(6)
                    .trim();

                continue;
            }

            if (line.startsWith("data:")) {
                dataLines.push(
                    line.slice(5).trimStart()
                );
            }
        }

        if (dataLines.length === 0) {
            return null;
        }

        return {
            type,
            data: JSON.parse(
                dataLines.join("\n")
            ),
        };
    }

    function resizeInput() {
        input.style.height = "auto";

        input.style.height = `${Math.min(
            input.scrollHeight,
            160
        )}px`;
    }

    input.addEventListener(
        "input",
        resizeInput
    );

    function hideSuggestions() {
        if (!suggestions) {
            return;
        }

        suggestions.hidden = true;
    }

    function addLoadingMessage() {
        const row = document.createElement("div");

        row.classList.add(
            "chat-row",
            "chat-row-assistant"
        );

        const avatar =
            document.createElement("div");

        avatar.classList.add(
            "chat-avatar"
        );

        avatar.textContent = "AI";
        avatar.setAttribute(
            "aria-hidden",
            "true"
        );

        const bubble =
            document.createElement("div");

        bubble.classList.add(
            "chat-message",
            "chat-message-assistant"
        );

        const loading =
            document.createElement("div");

        loading.classList.add(
            "chat-loading"
        );

        loading.setAttribute(
            "aria-label",
            language === "pl"
                ? "AI przygotowuje odpowiedź"
                : "AI is preparing an answer"
        );

        for (let i = 0; i < 3; i += 1) {
            const dot =
                document.createElement("span");

            dot.classList.add(
                "chat-loading-dot"
            );

            loading.appendChild(dot);
        }

        bubble.appendChild(loading);

        row.appendChild(avatar);
        row.appendChild(bubble);

        messages.appendChild(row);

        scrollToBottom();

        return row;
    }
});