from openai import OpenAI, AssistantEventHandler


class GptBrain:
    def __init__(self, token, model="gpt-4o-mini", assistant=None):
        self.client = OpenAI(
            api_key=token
        )
        self.model = model
        self.thread = None

        self.assistant = assistant

    def __call__(self, text, stream=False, keep_thread=False):
        """
        :param text: text to ask to gpt
        :param stream: using streaming print.
        :param keep_thread: if using assistant, check if you want to continue conversations.
        :return:
        """

        # if it is just a call, just make completion
        if self.assistant is None:
            thread = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": text,
                    }
                ],
                model=self.model,
                stream=stream
            )

            if stream:
                res = ""
                for chunk in thread:
                    content = chunk.choices[0].delta.content or ""
                    print(content, end="")
                    res += content
                return res

            else:
                return thread.choices[0].message.content

        else:
            if (not keep_thread) or (self.thread is None):
                self.thread = self.client.beta.threads.create()

            message = self.client.beta.threads.messages.create(
                thread_id=self.thread.id,
                role="user",
                content=text
            )

            if stream:
                self.cache = ""
                with self.client.beta.threads.runs.stream(
                    thread_id=self.thread.id,
                    assistant_id=self.assistant,
                    event_handler=self.EventHandler(self),
                ) as stream:
                    stream.until_done()
                return self.cache

            else:
                run = self.client.beta.threads.runs.create_and_poll(
                    thread_id=self.thread.id,
                    assistant_id=self.assistant
                )

                if run.status == 'completed':
                    messages = gpt.client.beta.threads.messages.list(
                        thread_id=self.thread.id
                    )
                    # print(messages.data)
                    return messages.data[0].content[0].text.value
                else:
                    # print(run.status)
                    return f"error code : {run.status}"

    # handler to stream assistant response, code from gpt document
    class EventHandler(AssistantEventHandler):
        def __init__(self, instance):
            super().__init__()
            self.instance = instance

        # @override
        def on_text_created(self, text) -> None:
            print(f"\n", end="", flush=True)

        # @override
        def on_text_delta(self, delta, snapshot):
            print(delta.value, end="", flush=True)
            self.instance.cache += delta.value

        def on_tool_call_created(self, tool_call):
            print(f"\n{tool_call.type}\n", flush=True)

        def on_tool_call_delta(self, delta, snapshot):
            if delta.type == 'code_interpreter':
                if delta.code_interpreter.input:
                    print(delta.code_interpreter.input, end="", flush=True)
                if delta.code_interpreter.outputs:
                    print(f"\n\noutput >", flush=True)
                    for output in delta.code_interpreter.outputs:
                        if output.type == "logs":
                            print(f"\n{output.logs}", flush=True)

