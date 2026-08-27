skills:
  - name: cloud_architecture_prototyping
    description: Designs scalable and highly available hosting environments using AWS managed services.
    input: functional requirements and estimated traffic load (Markdown or JSON format).
    output: A structured architectural plan including VPC, Compute (EC2/Beanstalk), and Database (RDS) layers.
    error_handling: If requirements are contradictory or exceed free-tier limits, the skill requests specific scaling priorities from the user.

  - name: predictive_model_evaluation
    description: Conducts comparative analysis across multiple machine learning classifiers to identify the most performant algorithm.
    input: Raw dataset features and target labels (CSV or Pandas DataFrame).
    output: Performance matrix including Accuracy, Precision, Recall, and F1-Score for each tested model.
    error_handling: If data is missing or non-numerical, it triggers a preprocessing sequence to handle null values or categorical encoding.

  - name: technical_presentation_structuring
    description: Translates complex cryptographic or big data concepts into organized, multi-slide seminar layouts.
    input: Technical whitepaper or raw algorithm logic (Text or PDF).
    output: A 15+ slide outline with logical flow, emphasizing visual design themes like grey and olive.
    error_handling: If the topic is too broad, it prompts the user to select specific sub-modules (e.g., "5 V's of Big Data") to maintain depth.