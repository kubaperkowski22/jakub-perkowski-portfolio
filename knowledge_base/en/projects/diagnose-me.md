---
id: project.diagnose-me
language: en
title: DiagnoseMe
source_type: project
source_slug: diagnose-me
source_path: /projekty/diagnose-me
visibility: public
---

# DiagnoseMe

## Project context and objective

DiagnoseMe was developed as part of my engineering thesis at Białystok University of Technology, entitled “Application Supporting Initial Medical Diagnosis and Recommendation of Further Treatment Using Elements of Artificial Intelligence.”

The goal was to create a Windows desktop application that enables users to complete a structured symptom interview and receive a preliminary assessment and suggestions for further action. The project combined traditional software engineering, a relational database, and an external language model. It did not involve training a proprietary medical model.

It was an academic prototype. It did not undergo clinical validation and is not a certified medical device. Generated information does not replace consultation with a doctor or a professional diagnosis.

## Architecture and technologies

I implemented the application in C# using WPF, with the interface defined in XAML. The project used the .NET platform, the MVVM pattern, and a separation between presentation, application logic, and data layers.

The main technologies and tools included:

- **WPF, XAML, and C#** — desktop interface and application logic.
- **CommunityToolkit.Mvvm** — support for MVVM and property-change notifications.
- **MahApps.Metro and MahApps.Metro.IconPacks** — interface controls, styling, and icons.
- **Entity Framework Core** — entity mapping, relational database operations, and migrations.
- **Azure SQL / SQL Server** — the cloud database used during the project.
- **Microsoft.Extensions.DependencyInjection** — dependency registration and management.
- **OpenAI API** — an external language model used for response generation.
- **Inno Setup Compiler** — preparation of the application installer.

MVVM helped separate views from ViewModels and application logic. Asynchronous operations, particularly API and database communication, helped keep the interface responsive while waiting for external services.

## Preliminary symptom-assessment workflow

The main feature was a multi-step interview. Users began with a form containing basic information such as year of birth, sex, height, and weight. They could then select symptoms from a list containing 31 items.

The next screen displayed follow-up questions associated with the selected symptoms. This meant the application did not need to ask every question of every user. The collected answers and basic information provided context for the language-model request.

The workflow can be summarized as follows:

```text
Basic user information
          ↓
Symptom selection
          ↓
Follow-up questions based on selected symptoms
          ↓
Prompt construction
          ↓
Asynchronous HTTP request to OpenAI API
          ↓
Response parsing and processing
          ↓
Preliminary assessment, description, and recommendations
          ↓
Optional result storage for a logged-in user
```

## Language-model integration

The AI module used a ready-made GPT model provided through the OpenAI API. Interview data was transformed into a prompt specifying the model's task and the expected response structure. The request was sent through an HTTP client, and the response was processed by the application.

The result was separated into the name of the identified disease or problem, a description, and recommendations for further action. This structure allowed the information to be displayed in separate interface sections and stored in the corresponding database fields.

The prompt also contained instructions to ignore empty answers or information unrelated to the interview. This was an attempt to limit unintended use, not a guarantee of resistance to prompt injection or other manipulation. The project did not use RAG, embeddings, or custom model training or fine-tuning.

## Data layer and additional features

The Azure SQL database stored user account information, diagnosis results, and appointment data. The thesis presents Users, Appointments, and DiagnosisResults entities, as well as an Entity Framework migration-history table. Relationships made it possible to associate stored results and appointments with individual users.

In addition to the main interview, the application included registration and login, a history of saved results, an appointment calendar, notifications, and account and theme settings. Logged-in users could view details of previous diagnoses and delete them. The calendar supported adding and deleting events, while notifications provided reminders about upcoming appointments.

The application also included a specialist-clinic search feature. This was an embedded NFZ website displayed in a browser control, not a custom integration with an NFZ API.

## Historical testing and deployment

As part of the thesis, I prepared an installer using Inno Setup Compiler. The deployment chapter describes installation, functional, and performance tests. The thesis reports successful installer tests on Windows 7, 10, and 11; this should not be interpreted as confirmation that the current code is fully compatible with all of these systems.

Functional tests included checking application behavior after installation and communication with the database and OpenAI API. An Internet connection was required to use the external services. The thesis also noted that the first connection to an Azure database that had been inactive for some time could take several seconds.

The thesis does not present a clinical evaluation of diagnostic accuracy against a reference dataset of medical cases or verified metrics such as diagnostic sensitivity, specificity, or accuracy. Application and installation tests are not equivalent to medical validation.

## Limitations and security

The result screen displayed a disclaimer stating that the generated diagnosis was not professional medical advice and that users should not rely solely on the recommendations. Results were intended to be verified by a doctor.

The thesis describes objectives concerning data protection, access control, and Azure firewall rules. However, this does not mean that a formal security audit, confirmed GDPR compliance, or clinical safety validation was performed.

The original repository contained credentials embedded in source code. During a later cleanup, I removed them from the current code and rewrote the public Git history. The old OpenAI key and Azure resources had already been decommissioned. The current code reads the required values from environment variables.

The project is not currently maintained as a running service. The original database and API key are no longer available, so cloning the repository alone is not sufficient to restore full functionality. A future public deployment would also require placing model access and sensitive services behind a controlled backend rather than distributing a shared API key in a desktop application.

## My contribution and skills gained

For the thesis, I designed and implemented the desktop application, its interface, interview workflow, OpenAI API integration, and data layer. I also developed additional application modules, prepared the installer, and carried out the tests described in the thesis.

The project gave me practical experience with C#, WPF, MVVM, external API integration, asynchronous programming, Entity Framework Core, SQL Server, and Azure. It also helped me understand how a language model can be integrated into a larger system in which input data is structured, responses are processed, and results are connected to application logic.

From an AI-engineering perspective, important lessons include the need for independent LLM quality evaluation, secure secret management, and a clear distinction between a technical prototype and a system intended for high-stakes use.

## Sources and scope

This document is based on my engineering thesis, “Application Supporting Initial Medical Diagnosis and Recommendation of Further Treatment Using Elements of Artificial Intelligence,” particularly Chapters 2–6. The description of the repository's current state and service decommissioning is based on subsequent actions confirmed by me.

Project repository: https://github.com/kubaperkowski22/DiagnoseMe

The document describes the historical prototype and its limitations. It contains no patient data, real login credentials, API keys, or connection strings. It is not medical documentation or an instruction manual for self-treatment.
