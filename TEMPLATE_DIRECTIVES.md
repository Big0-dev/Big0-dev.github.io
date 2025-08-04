# Template Directives Guide

This guide explains how to use template directives in markdown content files for services and industries pages.

## Available Template Directives

### 1. Call-to-Action Templates
Add pre-designed CTA sections to encourage user engagement:

```markdown
{{template:cta}}                 # General CTA
{{template:cta-service}}         # Service-specific CTA  
{{template:cta-case-study}}      # Case study CTA
```

### 2. Related Services
Link to related services in an attractive grid layout:

```markdown
{{related-services:service-slug1,service-slug2,service-slug3}}
```

Example:
```markdown
{{related-services:ai-integration,data-analytics,cloud-managment}}
```

### 3. Related Industries
Link to related industries:

```markdown
{{related-industries:industry-slug1,industry-slug2}}
```

Example:
```markdown
{{related-industries:finance,healthcare,retail,telecom}}
```

### 4. Industry Challenges (Industry Pages Only)
Display key challenges in a grid format:

```markdown
{{industry-challenges:Challenge 1|Challenge 2|Challenge 3}}
```

Example:
```markdown
{{industry-challenges:Complex regulatory requirements|Rising cybersecurity threats|Legacy system modernization}}
```

### 5. Industry Solutions (Industry Pages Only)
Display solutions with optional descriptions:

```markdown
{{industry-solutions:Solution Title|Description,Another Solution|Its description}}
```

Example:
```markdown
{{industry-solutions:Risk Management Platform|AI-powered credit risk assessment,Fraud Detection|Real-time monitoring}}
```

## Usage Tips

1. **Service Slugs**: Use the exact filename (without .md) from the services folder
   - Example: `ai-integration`, `cloud-managment`, `cybersecurity-solutions`

2. **Industry Slugs**: Use the exact filename (without .md) from the industries folder
   - Example: `finance`, `healthcare`, `retail`, `telecom`

3. **Formatting**: 
   - Use commas (,) to separate items in lists
   - Use pipes (|) to separate titles from descriptions or to separate challenges
   - Don't use special characters that might break the parser

4. **Placement**: Place directives on their own line with blank lines before and after for best results

## Examples

### Service Page Example
```markdown
## Our Advanced Solutions

We provide cutting-edge technology solutions...

{{related-industries:finance,healthcare,retail}}

## Why Choose Our Services

Our team delivers results...

{{template:cta-service}}
```

### Industry Page Example
```markdown
## Key Challenges We Address

{{industry-challenges:Regulatory compliance|Security threats|Digital transformation}}

## Our Solutions

{{industry-solutions:Banking Platform|Cloud-native architecture,Risk Analytics|Real-time assessment}}

{{related-services:ai-integration,cybersecurity-solutions}}
```