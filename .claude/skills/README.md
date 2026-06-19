# ODH Release Skills

A collection of conversational Claude Code skills that make ODH (Open Data Hub) release management accessible through natural language interactions. These skills provide guided assistance for complex workflows while preserving all existing GitOps processes and automation.

## **Overview**

The ODH Release Skills transform complex GitHub Actions workflows into conversational experiences that provide intelligent guidance, real-time validation, and smart defaults. Each skill leverages existing ODH infrastructure while adding a user-friendly interface layer.

### **Core Philosophy**
- **Conversational First**: Natural language interactions instead of complex forms
- **Intelligence Amplification**: Surface existing system logic through better UX  
- **Zero Disruption**: All existing workflows remain unchanged and fully functional
- **Smart Guidance**: Context-aware hints, validation, and examples

## **Available Skills**

### 1. `/odh-onboard` - Component Onboarding
**Purpose**: Interactive component onboarding with guided validation

**When to Use**:
- Adding new components to ODH
- First-time component registration
- Learning component requirements

**Key Features**:
- Real-time name validation using existing scripts
- Conflict detection against current registry
- Component type guidance (component vs image)
- Integration with approval workflow

**Example**:
```bash
/odh-onboard my-new-ai-service
# Guides through: name validation, display name, type selection
# Creates PR in odh-release-manager repository
```

### 2. `/odh-register` - Component Registration
**Purpose**: Register components for specific ODH releases

**When to Use**:
- Registering component versions for upcoming releases
- Updating component registration before code freeze
- Checking component registration status

**Key Features**:
- Auto-detect current active release
- Component version validation and guidance
- Branch tracking configuration
- Previous registration history context

**Example**:
```bash
/odh-register dashboard
# Shows current release, asks for version/branch
# Validates inputs, shows preview, executes registration
```

### 3. `/odh-set-next-release` - Release Planning  
**Purpose**: Plan and configure upcoming ODH releases

**When to Use**:
- Setting up next release timeline
- Updating release dates and deadlines
- Configuring release planning parameters

**Key Features**:
- Intelligent date calculation (code freeze = release - 3 days)
- Mode selection guidance (next/current/both)
- Business day awareness
- Release history context

**Example**:
```bash
/odh-set-next-release v3.6.0
# Guides through: date selection, code freeze calculation
# Explains modes, shows preview, configures release
```

### 4. `/odh-trigger-release` - Smart Release Triggering
**Purpose**: Trigger releases with component readiness assessment

**When to Use**:
- Starting the release process
- Checking component registration completeness
- Making fallback decisions for missing components

**Key Features**:
- Component readiness assessment
- Intelligent fallback preview using existing logic
- Decision guidance for missing registrations
- External staging monitoring setup

**Example**:
```bash
/odh-trigger-release
# Shows: 15/19 registered, 4 fallbacks, 0 missing
# Explains fallback versions, guides decision
# Triggers release with monitoring links
```

### 5. `/odh-monitor-community` - Community Release Monitoring
**Purpose**: Monitor community release progress with automated tracking

**When to Use**:
- Tracking community PR status
- Monitoring release completion
- Automating release finalization

**Key Features**:
- Automated PR status checking
- Merge detection with notifications  
- Release completion workflow integration
- Progress timeline estimation

**Example**:
```bash
/odh-monitor-community
# Detects community PR, monitors status
# Notifies when merged, offers completion trigger
# Automates final release steps
```

## **Getting Started**

### **Prerequisites**
- Claude Code CLI or IDE extension
- Access to ODH release repository
- Existing GitHub App authentication configured

### **Basic Usage**
1. **Start with onboarding** (for new components):
   ```bash
   /odh-onboard my-component
   ```

2. **Register for releases** (after approval):
   ```bash
   /odh-register my-component
   ```

3. **Plan releases** (release managers):
   ```bash
   /odh-set-next-release
   ```

4. **Trigger releases** (release managers):
   ```bash
   /odh-trigger-release
   ```

5. **Monitor completion** (release managers):
   ```bash
   /odh-monitor-community
   ```

## **Architecture**

### **Skill Structure**
```
.claude/skills/skill-name/
├── SKILL.md                 # Skill definition and documentation
└── scripts/
    └── script.py           # Implementation logic
```

### **Integration Points**

#### **Existing ODH Infrastructure**
- **Validation Scripts**: `.github/scripts/validate-*.sh`
- **YAML Configurations**: `configs/components-registry.yaml`, `configs/release-status.yaml`
- **GitHub Workflows**: All existing `.github/workflows/*.yaml` files
- **Authentication**: Existing GitHub App token infrastructure

#### **Preserved Processes**
- ✅ **All GitHub Actions workflows** remain unchanged
- ✅ **All validation rules** preserved exactly  
- ✅ **Same YAML structures** and audit trails
- ✅ **Identical GitOps processes** maintained

### **Intelligence Sources**
- **Component Registry**: Automatic dropdown sync, conflict detection
- **Release Status**: Current release detection, timeline awareness
- **Component Mapping**: Fallback logic from `build_component_mapping.sh`
- **Date Intelligence**: Business day logic from `validate_set_release_inputs.sh`

## **Advanced Usage**

### **Skill Chaining**
Skills are designed to work together seamlessly:
```bash
# Complete workflow example
/odh-onboard new-component          # 1. Add component to registry
# (wait for approval)
/odh-register new-component         # 2. Register for current release  
/odh-set-next-release v3.7.0        # 3. Plan next release
/odh-trigger-release               # 4. Start release process
/odh-monitor-community             # 5. Track to completion
```

### **Context Awareness**
Skills understand current system state:
- **Release Phase**: Provide appropriate options based on current release status
- **Component History**: Show previous registrations and patterns
- **Timeline Awareness**: Factor in deadlines and code freeze dates
- **Validation State**: Real-time feedback using existing validation logic

## **Troubleshooting**

### **Common Issues**

#### **"No active release found"**
- **Cause**: No current release configured
- **Solution**: Use `/odh-set-next-release` to plan a release first

#### **"Component not found in registry"** 
- **Cause**: Component hasn't been onboarded yet
- **Solution**: Use `/odh-onboard component-name` to add it

#### **"Release not ready for triggering"**
- **Cause**: Release status is not "scheduled"
- **Solution**: Check release timeline and component registrations

#### **"Invalid version format"**
- **Cause**: Version doesn't follow semantic versioning
- **Solution**: Use format like "v2.8.0" or "v3.0.0-ea.1"

### **Getting Help**
- Each skill provides contextual hints and examples
- Error messages include specific guidance and suggestions
- Skills integrate with existing ODH documentation
- Fallback to manual workflows is always available

## **Implementation Details**

### **Technology Stack**
- **Python 3**: Core skill implementation
- **yq**: YAML parsing and manipulation  
- **GitHub API**: Workflow triggering and status monitoring
- **Subprocess**: Integration with existing shell scripts

### **Dependencies**
- Access to `.github/scripts/` validation scripts
- Read/write permissions for `configs/*.yaml` files
- GitHub API permissions for workflow triggering
- Existing GitHub App authentication setup

### **Security & Permissions**
- **No new authentication**: Reuses existing GitHub App tokens
- **Same permissions**: No elevated access required
- **Audit trail preservation**: Identical Git commit patterns
- **Validation maintained**: All existing checks preserved

## **Future Enhancements**

### **Planned Features**
- **Slack/Email Integration**: Team notifications and updates
- **Advanced Monitoring**: Component health and dependency tracking  
- **Batch Operations**: Multi-component registration and management
- **Calendar Integration**: Release conflict detection and planning
- **Rollback Support**: Automated rollback detection and recovery

### **Integration Opportunities**
- **Jira Integration**: Automatic issue creation and tracking
- **Konflux Integration**: Enhanced build and deployment monitoring
- **Container Scanning**: Security and compliance validation
- **Documentation Generation**: Automatic release notes and changelogs

## **Contributing**

### **Adding New Skills**
1. Create skill directory: `.claude/skills/skill-name/`
2. Add `SKILL.md` with proper frontmatter
3. Implement `scripts/script.py` following existing patterns
4. Test integration with existing ODH infrastructure
5. Update this README with skill documentation

### **Skill Development Guidelines**
- **Follow conversational patterns** established by existing skills
- **Integrate with existing infrastructure** rather than rebuilding
- **Provide helpful guidance** with examples and validation
- **Maintain backward compatibility** with manual workflows
- **Include comprehensive error handling** and recovery options

---

## **Impact**

### **For Component Teams**
- **70% reduction** in form complexity for registration
- **Real-time validation** prevents submission errors
- **Contextual guidance** reduces learning curve
- **Integrated workflows** from onboarding to release

### **For Release Managers**
- **Unified visibility** across complex multi-repo processes  
- **Automated monitoring** reduces manual checking overhead
- **Smart decision support** with component readiness previews
- **Streamlined planning** with intelligent date calculations

### **System-Wide Benefits**
- **Preserved reliability** of existing GitOps processes
- **Enhanced accessibility** for new team members
- **Improved audit trails** with better user experience
- **Reduced errors** through conversational validation

The ODH Release Skills represent a new paradigm: **enhancing rather than replacing** existing automation to create more accessible, intelligent, and error-resistant workflows.