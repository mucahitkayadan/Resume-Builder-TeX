flowchart TD
    A[Start] --> B[User inputs job description]
    B --> C[Initialize ResumeCreator]
    C --> D[Load personal information and prompts]
    D --> E{Generate resume sections}
    E --> |For each section| F{Section type?}
    F --> |Hardcode| G[Use HardcodeSections]
    F --> |Process| H[Use AI Runner]
    G --> I[Add to content dictionary]
    H --> I
    I --> J{All sections processed?}
    J --> |No| E
    J --> |Yes| K[Create output directory]
    K --> L[Generate LaTeX content]
    L --> M[Compile LaTeX to PDF]
    M --> N[Save resume to database]
    N --> O[End]

    subgraph AI_Runner_Process
    P[Prepare prompt]
    Q[Send to AI model]
    R[Process AI response]
    P --> Q --> R
    end

    H --> AI_Runner_Process

    subgraph HardcodeSections_Process
    S[Load section data]
    T[Format data into LaTeX]
    S --> T
    end

    G --> HardcodeSections_Process
