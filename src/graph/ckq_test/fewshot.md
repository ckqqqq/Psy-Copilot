``` python


examples = [
    {
        "text": (
            "When clients reach a cognitive block and respond with ‘I don’t know’, "
            "therapists can provide suggestions based on case conceptualization or clinical experience to address the issue."
        ),
        "head": "clients reach a cognitive block and respond with ‘I don’t know’"
        "head_type": "Client Response",
        "relation": "Providing Suggestions",
        "tail": "Therapists can provide suggestions based on case conceptualization or clinical experience to address the issue.",
        "tail_type": "Therapist Strategy",
    },
    {
        "text": (
            """The therapist's suggestions can stimulate productive introspection in the client, but an excess of suggestions may lead to client passivity. It is important for the therapist to assess the client's response to suggestions to ensure genuine progress in therapy. Additionally, suggesting opposite thoughts can help clients explore their automatic thoughts and underlying beliefs."""
        ),
        "head": "An excess of therapist's suggestions may lead to client passivity",
        "head_type": "Client Issue",
        "relation": "Evaluate",
        "tail": "Therapist can assess client's response to suggestions for genuine progress and suggest opposite thoughts to explore automatic thoughts and underlying beliefs.",
        "tail_type": "Therapist Strategy",
    },
    {
        "text": (
            """The client’s response contains 'hot thoughts' that are closely linked to emotions and drive the emotional intensity. These thoughts are crucial in CBT for modification. Therapists focus on identifying and addressing these 'hot' automatic thoughts to understand the client's emotional reactions effectively. Encouraging clients to vividly imagine problematic situations can expedite the discovery of these 'hot' automatic thoughts. Asking clients about the worst possible outcomes can be an effective technique to elicit and address negative automatic thoughts, especially when they involve highly distorted future events. This approach can help clients develop adaptive responses and challenge catastrophic thinking patterns, as demonstrated in a scenario where a client with performance anxiety is prompted to consider the worst-case scenario."""
        ),
        "head": "A client with performance anxiety is prompted to consider the worst-case scenario.",
        "head_type": "Client Issue",
        "relation": "Evaluate",
        "tail": "Therapist can Identify and address 'hot thoughts', encourage vivid imagination of problematic situations, ask about worst possible outcomes, help develop adaptive responses, challenge catastrophic thinking.",
        "tail_type": "Therapist Strategy",
    },
    {
        "text": "来访者: 我好想减肥，但是我总是做不到。\n治疗师: 好吧，总是不断重新开始减肥的人基本上存在一个问题，那就是他们往往会很快放弃自己的减肥计划然后看着体重回升。",
        "head": "来访者的体重问题",
        "head_type": "Client Response",
        "relation": "Provide Suggestions",
        "tail": "治疗师建议制定合理饮食计划",
        "tail_type": "Therapist Response",
    },
    # {
    #     "text": "住院医生对病人的反应感到惊讶，并进一步探讨了病人对这种情况的内疚或良心的感觉。",
    #     "head": "病人的内疚或良心的感觉",
    #     "head_type": "Client Emotion",
    #     "relation": "Guide",
    #     "tail": "住院医生进一步探讨病人的情感反应",
    #     "tail_type": "Therapist Action"
    # },
    # {
    #     "text": "在以解决方案为中心的简短治疗中，探索杰克被治疗师盯上和尴尬的感受是必不可少的。通过了解杰克的观点和情绪，治疗师可以帮助他探索潜在的解决方案和应对策略。",
    #     "head": "在以解决方案为中心的简短治疗中，杰克的尴尬感受",
    #     "head_type": "Client Emotion",
    #     "relation": "Guide",
    #     "tail": "治疗师通过了解杰克的观点帮助杰克探索解决方案和应对策略",
    #     "tail_type": "Therapist Strategy"
    # },
    {
        "text": "鼓励来访者直接与保护性服务工作者交谈，阐明他们的期望，有助于依从性和决策。通过保持工作者作为孩子监护权的决策者，治疗师可以专注于支持来访者，而不会产生角色冲突。",
        "head": "治疗师产生角色冲突，无法专注于支持来访者",
        "head_type": "Counseling Issue",
        "relation": "Encourages",
        "tail": "治疗师鼓励来访者与保护性服务工作者直接交谈，从而可以专注于支持来访者",
        "tail_type": "Therapist Strategy"
    }
]
```