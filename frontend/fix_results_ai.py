content = open('C:\\Users\\eduma\\Desktop\\VerifiHireAI\\frontend\\src\\pages\\ResultsAI.js', 'r', encoding='utf-8').read()
target = '''            showToast('success', resp.data?.message || 'Qualification request submitted.');
            // Mark row as pending locally
            setAiAssessments(prev => prev.map(a =>
                String(a.id) === String(qualReasonPopup.aiSubmissionId)
                    ? { ...a, qual_pending: true }
                    : a
            ));
            setQualReasonPopup(null);
            setQualReason('');'''

replacement = '''            showToast('success', resp.data?.message || 'Qualification request submitted.');
            setQualReasonPopup(null);
            setQualReason('');
            fetchData();'''

if target in content:
    content = content.replace(target, replacement)
    open('C:\\Users\\eduma\\Desktop\\VerifiHireAI\\frontend\\src\\pages\\ResultsAI.js', 'w', encoding='utf-8').write(content)
    print('Replaced ResultsAI.js')
else:
    print('Not found in ResultsAI.js')
