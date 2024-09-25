# Todo 

### Milestore 1: Format notes using LLMs
- [ ] Create eval dataset to measure LLM judge performance
- [ ] Get LLM judge performance above 90% accuracy
- [ ] Get LLM editor performance above 90% accuracy 
- [ ] Investigate _reflection_ agentic workflow to improve LLM editor's performance

### System Design
- [ ] Create thin wrapper around `Completions` to reduce coupling: The `Completions` service return a `ChatCompletion object` which needs to be accessed to retrieve the LLM response. This currently forces us to have knowledge of the OpenAI's API across different modules  (e.g., `format_note()` service)

```python
>>> json_data: str = cast(str, chat_response.choices[0].message.content)
```

### Continuous Integration
- [ ] Start vLLM server during CI build (this is currently causing CI failures)

### Performance
- [ ] Threading or batching to maximize GPU utilization at inference time
