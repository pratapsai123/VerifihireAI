import sys

with open('backend/ai_candidates/views.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find the CandidateRegistrationUpdateView class and add face hash check before save()
for i, line in enumerate(lines):
    if 'class CandidateRegistrationUpdateView' in line:
        # Find the save() line within this class
        for j in range(i, min(i + 100, len(lines))):
            if 'candidate.save()' in lines[j] and j > i + 50:
                # Insert face hash check before save()
                indent = '            '
                new_lines = [
                    indent + "# SECURITY CHECK 4: Prevent same face from being used by multiple people\n",
                    indent + "face_embedding_hash = request.data.get('face_embedding_hash')\n",
                    indent + "if face_embedding_hash:\n",
                    indent + "    # Check if this face hash is already registered to another candidate\n",
                    indent + "    existing_face = Candidate.objects.filter(\n",
                    indent + "        face_embedding_hash=face_embedding_hash\n",
                    indent + "    ).exclude(public_token=public_token).first()\n",
                    indent + "\n",
                    indent + "    if existing_face:\n",
                    indent + "        return Response({\n",
                    indent + "            'error': f'This face is already registered to another candidate ({existing_face.full_name}). Each person can only register once.',\n",
                    indent + "            'duplicate_face': True,\n",
                    indent + "            'registered_to': existing_face.full_name\n",
                    indent + "        }, status=status.HTTP_400_BAD_REQUEST)\n",
                    indent + "\n",
                    indent + "    candidate.face_embedding_hash = face_embedding_hash\n",
                    indent + "\n",
                ]
                # Insert before save()
                for k, new_line in enumerate(new_lines):
                    lines.insert(j + k, new_line)
                print(f'Added face hash check at line {j + 1}')
                break
        break

with open('backend/ai_candidates/views.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print('SUCCESS: Face embedding hash duplicate check added to CandidateRegistrationUpdateView')
