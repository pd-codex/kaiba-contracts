// Plain-language narration over the same teaching model used by the technical view.
import {steps} from './walkthrough-model.mjs';

export const stories = {
  observe: {
    name: 'Get ready', act: 'A place in the fleet', headline: ['A new device.', 'A clean start.'],
    intro: 'Meet Device 01: a small computer waiting for a job. First, Kaiba checks it and prepares it for what comes next.',
    before: ['Just arrived', 'Its starting condition still needs checking.'], operation: ['Check & prepare', 'The provisioning team handles the setup.'], after: ['Prepared', 'Ready to have its identity checked.'],
    tasks: ['Check that this is the right device.', 'Apply its approved setup.', 'Keep a record of what happened.'],
    action: 'Prepare this device', busy: 'Preparing the device…', outcome: 'Setup is recorded. Next, Kaiba needs to check the device’s identity.',
    artifact: ['SETUP CHECKLIST', 'A recorded starting point'], icon: 'chip', note: 'This chapter includes the physical preparation. Later planning steps can happen without changing the software on the device.',
  },
  identity: {
    name: 'Check identity', act: 'A place in the fleet', headline: ['First, prove', 'who you are.'],
    intro: 'A familiar name is not enough. Kaiba checks the device’s own credentials before recognizing this particular device.',
    before: ['Identity pending', 'Prepared, but not yet recognized.'], operation: ['Verify its identity', 'The identity service checks its credentials.'], after: ['Identity recognized', 'This exact device now has an active identity.'],
    tasks: ['Ask the device to prove its identity.', 'Check its installed credentials.', 'Activate the verified identity.'],
    action: 'Check its identity', busy: 'Checking the credentials…', outcome: 'Identity recognized. Joining the fleet is a separate decision.',
    artifact: ['DEVICE PASSPORT', 'An identity of its own'], icon: 'identity', note: 'A replacement device has to establish its own identity. It cannot simply inherit the old device’s assignments.',
  },
  admit: {
    name: 'Join the fleet', act: 'A place in the fleet', headline: ['Welcome', 'to the fleet.'],
    intro: 'A fleet is a group of devices you manage together. Kaiba checks whether this device is allowed to join yours.',
    before: ['Recognized', 'Its identity is known; membership is pending.'], operation: ['Check membership', 'Kaiba checks ownership, suitability and current rules.'], after: ['A fleet member', 'Available to select for a configuration.'],
    tasks: ['Check which fleet it belongs to.', 'Check that it meets the fleet’s requirements.', 'Make it available as a configuration target.'],
    action: 'Check fleet membership', busy: 'Checking the fleet’s requirements…', outcome: 'Device 01 is a fleet member in this example. It is still waiting for a job.',
    artifact: ['FLEET MEMBERSHIP', 'One device, part of a group'], icon: 'fleet', note: 'Membership is checked again before important actions. A past approval does not override a later restriction.',
  },
  components: {
    name: 'Open the toolbox', act: 'Give it a job', headline: ['Big ideas.', 'Small building blocks.'],
    intro: 'Developers make reusable building blocks for jobs like collecting data or connecting to a service. Flow gives the operator a way to use them.',
    before: ['Waiting for a job', 'The device is a fleet member.'], operation: ['Prepare the toolbox', 'Developers define what each building block can do.'], after: ['Still waiting', 'The toolbox is ready. The device has not changed.'],
    tasks: ['Describe each building block’s settings.', 'Define how blocks connect safely.', 'Make reviewed versions available in Flow.'],
    action: 'Open the toolbox', busy: 'Gathering the building blocks…', outcome: 'The building blocks are ready to use. This work changes the shared toolbox, not the device.',
    artifact: ['THE TOOLBOX', 'Ready to connect'], icon: 'blocks', note: 'Developers can prepare this toolbox before a device arrives. Its place in this story is just to explain how the pieces fit.',
  },
  author: {
    name: 'Design the job', act: 'Give it a job', headline: ['Give it', 'a job to do.'],
    intro: 'In Flow, an operator connects building blocks into a recipe for the device. The recipe says what it should do.',
    before: ['No job selected', 'The device is ready for a plan.'], operation: ['Connect the blocks', 'The operator designs the job in Flow.'], after: ['A recipe is saved', 'It still needs checking for this device.'],
    tasks: ['Choose the building blocks.', 'Connect them and set their options.', 'Save a fixed version of the recipe.'],
    action: 'Save the recipe', busy: 'Saving the recipe…', outcome: 'A version of the recipe is saved. Editing the draft later will not silently change this version.',
    artifact: ['IN KAIBA FLOW', 'A recipe, not a running job'], icon: 'flow', note: 'The mini diagram is an illustration of authoring. Component and graph formats are still being designed; the device receives nothing at this step.',
  },
  resolve: {
    name: 'Review the plan', act: 'Give it a job', headline: ['See the plan.', 'Know what will change.'],
    intro: 'Kaiba combines the recipe with this device’s requirements. The operator reviews the exact device and settings before moving ahead.',
    before: ['Recipe saved', 'Device-specific checks are still needed.'], operation: ['Check & review', 'Kaiba works out the details; the operator reviews them.'], after: ['An exact plan', 'Reviewed for this device. Nothing is installed yet.'],
    tasks: ['Check the recipe against the device’s requirements.', 'Make conflicting or excluded choices visible.', 'Review the exact device and settings.'],
    action: 'Review this plan', busy: 'Putting the details together…', outcome: 'The operator has reviewed a plan for Device 01. A different device or changed settings need a new review.',
    artifact: ['PLAN REVIEW', '1 device · 1 reviewed plan'], icon: 'review', note: 'A fleet selection is pinned to exact devices during review. Devices that join later are not silently added to this publication.',
  },
  request: {
    name: 'Ask to publish', act: 'Make it official', headline: ['Happy with it?', 'Ask to publish.'],
    intro: 'The operator sends the reviewed plan to Kaiba. Asking to publish starts a decision; it does not install software.',
    before: ['Plan reviewed', 'The device is waiting for a decision.'], operation: ['Send the request', 'Flow asks Kaiba to accept this exact plan.'], after: ['Request sent', 'The device is still waiting.'],
    tasks: ['Use the exact plan the operator reviewed.', 'Send it with a stable request identity.', 'Wait for Kaiba’s acceptance decision.'],
    action: 'Send the publish request', busy: 'Sending the request to Kaiba…', outcome: 'The request reached Kaiba. It still needs to pass the final checks.',
    artifact: ['FLOW → KAIBA', 'A request for a decision'], icon: 'send', note: 'If the response goes missing, the same request can be recognized again. This helps prevent accidental duplicate work.',
  },
  accept: {
    name: 'Save the decision', act: 'Make it official', headline: ['Make the plan', 'official.'],
    intro: 'Kaiba checks that the reviewed plan still matches the current situation, then saves its acceptance so the work can be picked up later.',
    before: ['Decision pending', 'The device has received no new assignment.'], operation: ['Check & commit', 'Kaiba saves the decision and the work to follow.'], after: ['Plan published', 'Accepted and saved. The device has not updated yet.'],
    tasks: ['Check that the plan and permissions are still current.', 'Save one accepted publication and its follow-up work.', 'Return the confirmation to Flow.'],
    action: 'See Kaiba accept the plan', busy: 'Checking and saving the decision…', outcome: 'Plan published! The decision is saved, and work can resume from it later. The device is still waiting for rollout.',
    artifact: ['PUBLICATION RECEIPT', 'One saved decision'], icon: 'receipt', note: 'The accepted plan is durable even if a service restarts. Publishing the plan and confirming it is running remain separate milestones.',
  },
  fulfill: {
    name: 'What comes next', act: 'From plan to reality', headline: ['Published is', 'the beginning.'],
    intro: 'Next comes building, approving and delivering the software, then checking what actually runs. This story stops before that work happens.',
    before: ['Plan accepted', 'The device is waiting for rollout.'], operation: ['The work ahead', 'Build → approve → deliver → verify.'], after: ['Still waiting for rollout', 'No new software or running result is claimed here.'],
    tasks: ['Build the software and approve the exact release.', 'Assign it to this device and activate it safely.', 'Check device reports and independent evidence.'],
    action: 'See what happens next', busy: 'Looking at the next part of the journey…', outcome: 'You reached the end of the story. A saved plan is the starting point for a carefully checked rollout—not proof that the device has changed.',
    artifact: ['NEXT: ROLLOUT', 'Execution still ahead'], icon: 'launch', note: 'These later contracts are not implemented by this demo. A missing reply or an offline device never counts as a successful update.',
  },
};

export const storyScenarios = {
  reviewed: ['The complete journey', 'Explore the intended process with the example checks assumed to pass.'],
  development: ['What if it is lab-only?', 'A lab device can be prepared, but it cannot pass the production identity gate.'],
  conflict: ['What if someone changes the plan?', 'Another assignment arrives after review. Kaiba must not overwrite it silently.'],
  lost: ['What if the confirmation gets lost?', 'Kaiba saves the decision, but Flow loses the reply. Recover it without publishing twice.'],
};

export function storyFor(state) {
  const id = steps[state.step].id;
  const base = stories[id];
  const story = {...base, tasks: [...base.tasks]};
  const result = state.results[id];
  if (state.scenario === 'development' && id === 'observe') {
    story.after = ['Prepared for the lab', 'Production qualification is still missing.'];
    story.outcome = 'This device is prepared for development work. That does not make it ready for production.';
  }
  if (state.scenario === 'development' && id === 'identity') {
    story.before = ['Lab-only device', 'It is missing production qualification.'];
    story.tasks = ['Read its lab-only status.', 'Check whether production use is permitted.', 'Stop before activating a production identity.'];
    story.after = ['Still lab-only', 'Its identity and fleet access stay unchanged.'];
    if (result) story.headline = ['This device', 'stays in the lab.'];
    story.outcome = 'Kaiba stops here because this device is not qualified for production. Preparation alone cannot grant it an active production identity.';
    story.artifact = ['PRODUCTION CHECK', 'More qualification needed'];
  }
  if (state.scenario === 'conflict' && id === 'accept') {
    story.before = ['A newer assignment exists', 'Someone changed the device’s assignment after your review.'];
    story.tasks = ['Read the device’s current assignment.', 'Spot that it differs from the reviewed version.', 'Reject this request and require a new review.'];
    story.after = ['Nothing overwritten', 'The newer assignment stays in place.'];
    story.outcome = 'Someone else got there first. Kaiba rejects this request so it cannot overwrite their assignment. The operator needs to review a new plan.';
    story.artifact = ['PLAN CHANGED', 'A new review is needed'];
    if (result) story.headline = ['A newer plan', 'got there first.'];
  }
  if (state.scenario === 'lost' && id === 'accept') {
    story.tasks[2] = 'The confirmation gets lost on its way back to Flow.';
    if (result?.kind === 'unknown') {
      story.headline = ['Saved. But the', 'reply went missing.'];
      story.after = ['Saved once by Kaiba', 'Flow does not know the outcome yet.'];
      story.outcome = 'Kaiba saved the plan once, but Flow missed the reply. Recover the confirmation using the same request; do not create another publication.';
      story.artifact = ['CONFIRMATION MISSING', 'Saved once · reply unknown'];
    } else if (state.retries) {
      story.headline = ['One plan.', 'Confirmation recovered.'];
      story.tasks.push('Use the identical request to recover the saved confirmation.');
      story.after = ['Confirmation recovered', 'The same publication. Still only one saved decision.'];
      story.outcome = 'Flow recovered the original confirmation. Kaiba did not publish a second plan, and the device itself has not changed.';
      story.artifact = ['CONFIRMATION RECOVERED', 'Still one saved decision'];
    }
  }
  return story;
}
