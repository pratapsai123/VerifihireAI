import sys

with open('backend/ai_candidates/views.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Replace lines 3922-3928 (0-indexed: 3921-3927)
new_lines = lines[:3921]

# Add new PAN handling with security checks
new_lines.append("            pan_number = request.data.get('pan_number')\n")
new_lines.append("            if pan_number:\n")
new_lines.append("                pan_number = pan_number.upper().strip()\n")
new_lines.append("                pan_pattern = r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$'\n")
new_lines.append("                if not re.match(pan_pattern, pan_number):\n")
new_lines.append("                    return Response({'error': 'Invalid PAN format. Expected: ABCDE1234F'}, status=status.HTTP_400_BAD_REQUEST)\n")
new_lines.append("\n")
new_lines.append("                # SECURITY CHECK 1: Prevent PAN changes after interview starts\n")
new_lines.append("                if candidate.pan_locked:\n")
new_lines.append("                    return Response({\n")
new_lines.append("                        'error': 'PAN number cannot be changed once the interview has started.',\n")
new_lines.append("                        'pan_locked': True\n")
new_lines.append("                    }, status=status.HTTP_400_BAD_REQUEST)\n")
new_lines.append("\n")
new_lines.append("                # SECURITY CHECK 2: Prevent one person from using multiple PANs\n")
new_lines.append("                if candidate.pan_number and candidate.pan_number != pan_number:\n")
new_lines.append("                    return Response({\n")
new_lines.append("                        'error': 'PAN number cannot be changed. You already registered with a different PAN.',\n")
new_lines.append("                        'existing_pan': candidate.pan_number\n")
new_lines.append("                    }, status=status.HTTP_400_BAD_REQUEST)\n")
new_lines.append("\n")
new_lines.append("                # SECURITY CHECK 3: Prevent multiple people from using same PAN\n")
new_lines.append("                existing_candidate = Candidate.objects.filter(\n")
new_lines.append("                    pan_number=pan_number\n")
new_lines.append("                ).exclude(public_token=public_token).first()\n")
new_lines.append("\n")
new_lines.append("                if existing_candidate:\n")
new_lines.append("                    return Response({\n")
new_lines.append("                        'error': f'This PAN number ({pan_number}) is already registered to {existing_candidate.full_name} ({existing_candidate.email}). Each PAN can only be used for one interview.',\n")
new_lines.append("                        'duplicate': True,\n")
new_lines.append("                        'registered_to': existing_candidate.full_name\n")
new_lines.append("                    }, status=status.HTTP_400_BAD_REQUEST)\n")
new_lines.append("\n")
new_lines.append("                # Track PAN history for audit\n")
new_lines.append("                if not candidate.pan_number:\n")
new_lines.append("                    from django.utils import timezone\n")
new_lines.append("                    candidate.pan_history = [{\n")
new_lines.append("                        'action': 'registered',\n")
new_lines.append("                        'pan': pan_number,\n")
new_lines.append("                        'timestamp': timezone.now().isoformat()\n")
new_lines.append("                    }]\n")
new_lines.append("\n")
new_lines.append("                candidate.pan_number = pan_number\n")

# Add remaining lines after line 3928
new_lines.extend(lines[3928:])

with open('backend/ai_candidates/views.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print('SUCCESS: PAN security checks added to CandidateRegistrationUpdateView')
