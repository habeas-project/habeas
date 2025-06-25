import React, { useEffect, useState } from "react";
import {
  View,
  Text,
  Modal,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  ActivityIndicator,
  Alert,
  TextInput,
  KeyboardAvoidingView,
  Platform,
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";

import { getCaseDetails, acceptCase, DetailedCaseResponse, AttorneyCaseAcceptanceResponse } from "../api/client";
import { useAuth } from "../contexts/AuthContext";

interface CaseDetailModalProps {
  visible: boolean;
  caseId: number | null;
  onClose: () => void;
  onAccept: (caseId: number) => Promise<void>;
}

const CaseDetailModal: React.FC<CaseDetailModalProps> = ({ visible, caseId, onClose, onAccept }) => {
  const { user } = useAuth();
  const [caseDetails, setCaseDetails] = useState<DetailedCaseResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [accepting, setAccepting] = useState(false);
  const [attorneyMessage, setAttorneyMessage] = useState("");
  const [showMessageInput, setShowMessageInput] = useState(false);
  const [acceptanceResult, setAcceptanceResult] = useState<AttorneyCaseAcceptanceResponse | null>(null);

  // Load case details when modal opens
  useEffect(() => {
    if (visible && caseId) {
      loadCaseDetails();
    } else {
      // Reset state when modal closes
      setCaseDetails(null);
      setAcceptanceResult(null);
      setAttorneyMessage("");
      setShowMessageInput(false);
    }
  }, [visible, caseId]);

  const loadCaseDetails = async (): Promise<void> => {
    if (!caseId) return;

    setLoading(true);
    try {
      const details = await getCaseDetails(caseId);
      setCaseDetails(details);
    } catch (error) {
      console.error('Failed to load case details:', error);
      Alert.alert('Error', 'Failed to load case details. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleAcceptCase = (): void => {
    setShowMessageInput(true);
  };

  const confirmAcceptCase = async (): Promise<void> => {
    if (!caseDetails || !user?.id) return;

    setAccepting(true);
    try {
      const result = await acceptCase(
        caseDetails.case_id,
        user.id,
        { message: attorneyMessage.trim() || undefined }
      );

      setAcceptanceResult(result);

      // Call the parent's onAccept callback
      await onAccept(caseDetails.case_id);

      Alert.alert(
        'Case Accepted',
        result.message,
        [{ text: 'View Contact Info', onPress: () => setShowMessageInput(false) }]
      );
    } catch (error) {
      console.error('Failed to accept case:', error);
      Alert.alert('Error', 'Failed to accept case. Please try again.');
      setShowMessageInput(false);
    } finally {
      setAccepting(false);
    }
  };

  const getUrgencyColor = (urgency: string): string => {
    switch (urgency) {
      case 'urgent': return '#dc2626';
      case 'high': return '#ea580c';
      case 'medium': return '#d97706';
      case 'low': return '#65a30d';
      default: return '#6b7280';
    }
  };

  const formatCaseType = (caseType: string): string => {
    return caseType === 'self' ? 'Self-Representation' : 'Loved One';
  };

  const renderContactInfo = (): JSX.Element | null => {
    if (!acceptanceResult?.client_contact_info) return null;

    const { client_info, emergency_contacts } = acceptanceResult.client_contact_info;

    return (
      <View style={styles.contactSection}>
        <Text style={styles.sectionTitle}>📞 Contact Information</Text>

        <View style={styles.contactCard}>
          <Text style={styles.contactName}>
            {client_info.first_name} {client_info.last_name}
          </Text>
          {client_info.phone_number && (
            <Text style={styles.contactDetail}>📱 {client_info.phone_number}</Text>
          )}
          {client_info.email && (
            <Text style={styles.contactDetail}>📧 {client_info.email}</Text>
          )}
        </View>

        {emergency_contacts && emergency_contacts.length > 0 && (
          <>
            <Text style={styles.subSectionTitle}>Emergency Contacts</Text>
            {emergency_contacts.map((contact, index) => (
              <View key={index} style={styles.contactCard}>
                <Text style={styles.contactName}>{contact.name}</Text>
                <Text style={styles.contactRelation}>{contact.relationship}</Text>
                <Text style={styles.contactDetail}>📱 {contact.phone}</Text>
                {contact.email && (
                  <Text style={styles.contactDetail}>📧 {contact.email}</Text>
                )}
              </View>
            ))}
          </>
        )}

        {acceptanceResult.client_contact_info.case_notes && (
          <>
            <Text style={styles.subSectionTitle}>Case Notes</Text>
            <Text style={styles.caseNotes}>
              {acceptanceResult.client_contact_info.case_notes}
            </Text>
          </>
        )}
      </View>
    );
  };

  if (loading) {
    return (
      <Modal visible={visible} animationType="slide" onRequestClose={onClose}>
        <SafeAreaView style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#007AFF" />
          <Text style={styles.loadingText}>Loading case details...</Text>
        </SafeAreaView>
      </Modal>
    );
  }

  return (
    <Modal visible={visible} animationType="slide" onRequestClose={onClose}>
      <SafeAreaView style={styles.container}>
        <KeyboardAvoidingView
          style={styles.container}
          behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        >
          {/* Header */}
          <View style={styles.header}>
            <TouchableOpacity onPress={onClose} style={styles.closeButton}>
              <Text style={styles.closeButtonText}>✕</Text>
            </TouchableOpacity>
            <Text style={styles.headerTitle}>Case Details</Text>
            <View style={styles.headerSpacer} />
          </View>

          {caseDetails ? (
            <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
              {/* Case Overview */}
              <View style={styles.section}>
                <View style={styles.caseHeader}>
                  <View style={[styles.urgencyBadge, { backgroundColor: getUrgencyColor(caseDetails.urgency_level) }]}>
                    <Text style={styles.urgencyText}>{caseDetails.urgency_level.toUpperCase()}</Text>
                  </View>
                  <Text style={styles.caseId}>Case #{caseDetails.case_id}</Text>
                </View>

                <Text style={styles.clientName}>
                  {caseDetails.client_info.first_name} {caseDetails.client_info.last_name}
                </Text>
                <Text style={styles.caseType}>
                  {caseDetails.case_type === 'self' ? '👤' : '👥'} {formatCaseType(caseDetails.case_type)}
                </Text>
                <Text style={styles.timeCreated}>⏰ {caseDetails.time_since_created}</Text>
              </View>

              {/* Location Information */}
              <View style={styles.section}>
                <Text style={styles.sectionTitle}>📍 Location</Text>
                <Text style={styles.locationText}>
                  {caseDetails.detention_location.description}
                </Text>
                {caseDetails.detention_location.city && caseDetails.detention_location.state && (
                  <Text style={styles.locationSubtext}>
                    {caseDetails.detention_location.city}, {caseDetails.detention_location.state}
                  </Text>
                )}
              </View>

              {/* Court Information */}
              <View style={styles.section}>
                <Text style={styles.sectionTitle}>⚖️ Court</Text>
                <Text style={styles.courtName}>{caseDetails.court_info.court_name}</Text>
                <Text style={styles.courtAbbreviation}>
                  {caseDetails.court_info.court_abbreviation}
                </Text>
                {caseDetails.court_info.district_court_contact?.phone && (
                  <Text style={styles.courtContact}>
                    📞 {caseDetails.court_info.district_court_contact.phone}
                  </Text>
                )}
                {caseDetails.court_info.district_court_contact?.email && (
                  <Text style={styles.courtContact}>
                    📧 {caseDetails.court_info.district_court_contact.email}
                  </Text>
                )}
              </View>

              {/* Status Information */}
              <View style={styles.section}>
                <Text style={styles.sectionTitle}>📊 Status</Text>
                <Text style={styles.statusText}>
                  Status: {caseDetails.status.replace('_', ' ').toUpperCase()}
                </Text>
                <Text style={styles.notificationCount}>
                  {caseDetails.attorneys_notified_count} attorneys notified
                </Text>
              </View>

              {/* Case Notes */}
              {caseDetails.case_notes && (
                <View style={styles.section}>
                  <Text style={styles.sectionTitle}>📝 Notes</Text>
                  <Text style={styles.caseNotesText}>{caseDetails.case_notes}</Text>
                </View>
              )}

              {/* Contact Information (shown after acceptance) */}
              {renderContactInfo()}

              {/* Attorney Message Input */}
              {showMessageInput && (
                <View style={styles.section}>
                  <Text style={styles.sectionTitle}>✍️ Message to Client (Optional)</Text>
                  <TextInput
                    style={styles.messageInput}
                    placeholder="Add a personal message to introduce yourself..."
                    value={attorneyMessage}
                    onChangeText={setAttorneyMessage}
                    multiline
                    numberOfLines={4}
                    maxLength={500}
                  />
                  <Text style={styles.characterCount}>
                    {attorneyMessage.length}/500 characters
                  </Text>
                </View>
              )}
            </ScrollView>
          ) : (
            <View style={styles.errorContainer}>
              <Text style={styles.errorText}>Case details not available</Text>
            </View>
          )}

          {/* Action Buttons */}
          {caseDetails && (
            <View style={styles.actionContainer}>
              {!showMessageInput && !acceptanceResult ? (
                <TouchableOpacity
                  style={styles.acceptButton}
                  onPress={handleAcceptCase}
                  disabled={caseDetails.status !== 'active'}
                >
                  <Text style={styles.acceptButtonText}>
                    {caseDetails.status === 'active' ? 'Accept Case' : 'Case No Longer Available'}
                  </Text>
                </TouchableOpacity>
              ) : showMessageInput ? (
                <View style={styles.confirmButtons}>
                  <TouchableOpacity
                    style={styles.cancelButton}
                    onPress={() => setShowMessageInput(false)}
                    disabled={accepting}
                  >
                    <Text style={styles.cancelButtonText}>Cancel</Text>
                  </TouchableOpacity>
                  <TouchableOpacity
                    style={[styles.confirmButton, accepting && styles.disabledButton]}
                    onPress={confirmAcceptCase}
                    disabled={accepting}
                  >
                    {accepting ? (
                      <ActivityIndicator size="small" color="white" />
                    ) : (
                      <Text style={styles.confirmButtonText}>Confirm Acceptance</Text>
                    )}
                  </TouchableOpacity>
                </View>
              ) : (
                <TouchableOpacity style={styles.acceptedButton} disabled>
                  <Text style={styles.acceptedButtonText}>✓ Case Accepted</Text>
                </TouchableOpacity>
              )}
            </View>
          )}
        </KeyboardAvoidingView>
      </SafeAreaView>
    </Modal>
  );
};

const styles = StyleSheet.create({
  acceptButton: {
    alignItems: 'center',
    backgroundColor: '#059669',
    borderRadius: 12,
    padding: 16,
  },
  acceptButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
  },
  acceptedButton: {
    alignItems: 'center',
    backgroundColor: '#10b981',
    borderRadius: 12,
    padding: 16,
  },
  acceptedButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
  },
  actionContainer: {
    backgroundColor: 'white',
    borderTopColor: '#e5e7eb',
    borderTopWidth: 1,
    paddingHorizontal: 20,
    paddingVertical: 16,
  },
  cancelButton: {
    alignItems: 'center',
    backgroundColor: '#f3f4f6',
    borderRadius: 12,
    flex: 1,
    padding: 16,
  },
  cancelButtonText: {
    color: '#374151',
    fontSize: 16,
    fontWeight: 'bold',
  },
  caseHeader: {
    alignItems: 'center',
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 12,
  },
  caseId: {
    color: '#6b7280',
    fontSize: 14,
    fontWeight: '500',
  },
  caseNotes: {
    backgroundColor: 'white',
    borderRadius: 8,
    color: '#374151',
    fontSize: 14,
    lineHeight: 18,
    padding: 12,
  },
  caseNotesText: {
    color: '#374151',
    fontSize: 15,
    lineHeight: 20,
  },
  caseType: {
    color: '#374151',
    fontSize: 16,
    marginBottom: 4,
  },
  characterCount: {
    color: '#6b7280',
    fontSize: 12,
    marginTop: 4,
    textAlign: 'right',
  },
  clientName: {
    color: '#1f2937',
    fontSize: 20,
    fontWeight: 'bold',
    marginBottom: 4,
  },
  closeButton: {
    backgroundColor: '#f3f4f6',
    borderRadius: 20,
    padding: 8,
  },
  closeButtonText: {
    color: '#6b7280',
    fontSize: 18,
    fontWeight: 'bold',
  },
  confirmButton: {
    alignItems: 'center',
    backgroundColor: '#059669',
    borderRadius: 12,
    flex: 2,
    padding: 16,
  },
  confirmButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
  },
  confirmButtons: {
    flexDirection: 'row',
    gap: 12,
  },
  contactCard: {
    backgroundColor: 'white',
    borderRadius: 8,
    marginBottom: 8,
    padding: 12,
  },
  contactDetail: {
    color: '#374151',
    fontSize: 14,
    marginBottom: 2,
  },
  contactName: {
    color: '#1f2937',
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 4,
  },
  contactRelation: {
    color: '#0ea5e9',
    fontSize: 14,
    fontWeight: '500',
    marginBottom: 4,
  },
  contactSection: {
    backgroundColor: '#f0f9ff',
    borderColor: '#0ea5e9',
    borderWidth: 1,
  },
  container: {
    backgroundColor: '#f8f9fa',
    flex: 1,
  },
  content: {
    flex: 1,
    paddingHorizontal: 20,
  },
  courtAbbreviation: {
    color: '#6b7280',
    fontSize: 14,
    marginBottom: 8,
  },
  courtContact: {
    color: '#374151',
    fontSize: 14,
    marginBottom: 2,
  },
  courtName: {
    color: '#374151',
    fontSize: 16,
    fontWeight: '500',
    marginBottom: 4,
  },
  disabledButton: {
    opacity: 0.6,
  },
  errorContainer: {
    alignItems: 'center',
    flex: 1,
    justifyContent: 'center',
  },
  errorText: {
    color: '#6b7280',
    fontSize: 16,
  },
  header: {
    alignItems: 'center',
    backgroundColor: 'white',
    borderBottomColor: '#e5e7eb',
    borderBottomWidth: 1,
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingHorizontal: 20,
    paddingVertical: 16,
  },
  headerSpacer: {
    width: 36,
  },
  headerTitle: {
    color: '#1f2937',
    fontSize: 18,
    fontWeight: 'bold',
  },
  loadingContainer: {
    alignItems: 'center',
    backgroundColor: '#f8f9fa',
    flex: 1,
    justifyContent: 'center',
  },
  loadingText: {
    color: '#6b7280',
    fontSize: 16,
    marginTop: 12,
  },
  locationSubtext: {
    color: '#6b7280',
    fontSize: 14,
    marginTop: 4,
  },
  locationText: {
    color: '#374151',
    fontSize: 16,
    lineHeight: 22,
  },
  messageInput: {
    backgroundColor: 'white',
    borderColor: '#d1d5db',
    borderRadius: 8,
    borderWidth: 1,
    fontSize: 16,
    minHeight: 100,
    padding: 12,
    textAlignVertical: 'top',
  },
  notificationCount: {
    color: '#6b7280',
    fontSize: 14,
  },
  section: {
    backgroundColor: 'white',
    borderRadius: 12,
    elevation: 2,
    marginVertical: 8,
    padding: 16,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 1,
    },
    shadowOpacity: 0.1,
    shadowRadius: 2,
  },
  sectionTitle: {
    color: '#1f2937',
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 8,
  },
  statusText: {
    color: '#374151',
    fontSize: 16,
    fontWeight: '500',
    marginBottom: 4,
  },
  subSectionTitle: {
    color: '#374151',
    fontSize: 14,
    fontWeight: '600',
    marginBottom: 8,
    marginTop: 12,
  },
  timeCreated: {
    color: '#6b7280',
    fontSize: 14,
  },
  urgencyBadge: {
    borderRadius: 12,
    paddingHorizontal: 8,
    paddingVertical: 4,
  },
  urgencyText: {
    color: 'white',
    fontSize: 12,
    fontWeight: 'bold',
  },
});

export default CaseDetailModal;
