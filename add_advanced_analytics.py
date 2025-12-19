"""
Script to add AdvancedAnalytics component to App.tsx
"""
import re

# Read the file
with open('frontend/src/App.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the position to insert the component (after the last </div> before the closing of analysis tab)
# Look for the pattern that indicates end of existing charts section
pattern = r'(</div>\s*</div>\s*</div>\s*\)\}\s*</div>)'

# Check if AdvancedAnalytics is already added
if 'AdvancedAnalytics' not in content or '<AdvancedAnalytics' not in content:
    # Find the position
    match = re.search(pattern, content)
    if match:
        # Insert before the last closing divs
        insert_pos = content.rfind('</div>\n                    </div>\n                )}\n            </div>')
        
        if insert_pos > 0:
            # Create the component call
            component_call = '''
                        {/* Advanced Analytics Section */}
                        <AdvancedAnalytics
                            timeSeriesQuality={timeSeriesQuality}
                            clerkPerformance={clerkPerformance}
                            vehicleUtilization={vehicleUtilization}
                            heatmapData={heatmapData}
                            comparativeAnalysis={comparativeAnalysis}
                            predictiveTrends={predictiveTrends}
                        />
'''
            
            # Find the right position (before the closing </div> of the analysis tab content)
            # Look for the pattern: </div>\n                    </div>\n                )}
            analysis_end = content.rfind('</div>\n                    </div>\n                )}\n            </div>')
            
            if analysis_end > 0:
                # Insert before the second-to-last </div>
                insert_point = content.rfind('</div>\n                    </div>', 0, analysis_end)
                
                if insert_point > 0:
                    new_content = content[:insert_point] + component_call + content[insert_point:]
                    
                    # Write back
                    with open('frontend/src/App.tsx', 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    
                    print("✅ Successfully added AdvancedAnalytics component to App.tsx")
                else:
                    print("❌ Could not find insertion point")
            else:
                print("❌ Could not find analysis tab end")
        else:
            print("❌ Could not find pattern")
    else:
        print("❌ Pattern not found")
else:
    print("ℹ️  AdvancedAnalytics component already exists in App.tsx")
