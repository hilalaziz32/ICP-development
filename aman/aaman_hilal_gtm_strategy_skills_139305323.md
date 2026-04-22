# Aaman / Hilal. GTM Strategy skills

- **Scheduled:** 2026-04-20T13:00:00Z
- **Recorded:** 2026-04-20T13:22:53Z
- **Recorded by:** Hilal Aziz <hilal@scaletopia.io> (None)
- **Share URL:** https://fathom.video/share/mBeTKXC47THvybNzDrkzcjmkbsXbxc41
- **Recording ID:** 139305323

## Participants
- Aaman Ahmed <aaman@consultscaletopia.com> (external)
- Hilal Aziz <hilal@scaletopia.io>

## Summary
### [Automation goal for copy creation @ 0:45](https://fathom.video/share/mBeTKXC47THvybNzDrkzcjmkbsXbxc41?tab=summary&timestamp=45)

Aaman proposes automating 90% of email and SMS copy creation by end of week, identifying copy creation (not strategy) as the most time-consuming bottleneck. He plans to document the GTM strategy process via Loom recording to demonstrate the workflow, and seeks Hilal's input on the approach.

### [AI playbook system architecture @ 1:52](https://fathom.video/share/mBeTKXC47THvybNzDrkzcjmkbsXbxc41?tab=summary&timestamp=112)

Hilal presents a comprehensive playbook system where AI uses structured prompts to generate copy based on ICP and GTM strategy inputs. The system includes integrated tools: Fathom (to gather email transcripts and meeting context) and a Slack tool (to collect channel conversations), ensuring AI has full context about client operations. The playbook contains all GTM strategist skills that can be individually selected and executed with appropriate prerequisites provided to AI.

### [Modular skill structure and folder organization @ 4:02](https://fathom.video/share/mBeTKXC47THvybNzDrkzcjmkbsXbxc41?tab=summary&timestamp=242)

Aaman proposes creating separate agents/skills for each copywriting type (email, SMS) and research, with a parent folder containing shared onboarding docs, call transcripts, and ICP to avoid repetition. Hilal confirms this is already implemented: all skills and SOPs are modular with SMS copy linked to SMS rules, email copy linked to email guidelines, and everything connected behind the scenes. The output structure automatically creates five context folders (transcripts, Slack conversations, Fathom meetings, onboarding sheet, form answers) plus a "Client's Output by AI" folder containing all AI-generated deliverables.

### [GitHub integration and team collaboration @ 5:33](https://fathom.video/share/mBeTKXC47THvybNzDrkzcjmkbsXbxc41?tab=summary&timestamp=333)

Hilal explains the system uses GitHub integration where team members (Khizar, Fahad) can pull the latest repository structure via GitPull, automatically syncing any updates to client output folders without requiring manual sharing. This allows Aaman to make changes independently while keeping the team's local copies current.

### [Technical implementation and best practices @ 7:03](https://fathom.video/share/mBeTKXC47THvybNzDrkzcjmkbsXbxc41?tab=summary&timestamp=423)

Six structured prompts guide each step of the GTM strategy process. Critical best practice: use a new chat for each skill to prevent context window overload and AI hallucination, as outputs are automatically saved to files for reference in subsequent prompts. Additional tools enabled include Gina AI search for customized research (Reddit threads, Facebook posts, etc.), allowing AI to conduct independent research or use specialized search capabilities.

### [Data accuracy and iterative improvement @ 8:21](https://fathom.video/share/mBeTKXC47THvybNzDrkzcjmkbsXbxc41?tab=summary&timestamp=501)

Aaman raises concerns that some offer and value prop data in the skills may be outdated and wants to review during the 7:30 walkthrough. Hilal notes the system is flexible—Aaman can use voice prompting to update skills, treating the playbook as a living document that improves over time through iterative refinement.

### [Next steps and single-client pilot @ 8:48](https://fathom.video/share/mBeTKXC47THvybNzDrkzcjmkbsXbxc41?tab=summary&timestamp=528)

Aaman requests a detailed walkthrough at the 7:30 call to see the system in action using Kinship as the test client. The team agrees to focus on one client this week to measure results and validate the approach before scaling. Hilal will demonstrate the six prompts and walk through the workflow, while Aaman will review and update any outdated skill content.

## Transcript
**[00:00:00] Aaman A:** Yo, Hilal.
**[00:00:04] Hilal Aziz:** Yeah, yeah, yeah, hello, How's going, bro?
**[00:00:09] Aaman A:** Let me look at your calendar.
**[00:00:15] Aaman A:** Do you have time on...
**[00:00:16] Aaman A:** Let me see your time.
**[00:00:19] Hilal Aziz:** I have time.
**[00:00:21] Hilal Aziz:** Let me check something.
**[00:00:22] Aaman A:** Because I have a call with Jordan, our advisor, like, right after this.
**[00:00:26] Aaman A:** I just think, I don't want to rush our call at all.
**[00:00:31] Aaman A:** 7.30.
**[00:00:33] Hilal Aziz:** Yeah, it works for me.
**[00:00:35] Hilal Aziz:** Good, man.
**[00:00:36] Hilal Aziz:** Okay, wait.
**[00:00:36] Aaman A:** 7.30.
**[00:00:38] Aaman A:** Yeah, 7.30 works.
**[00:00:39] Aaman A:** Cool, that works.
**[00:00:41] Aaman A:** let's list, I'm going to, let me just push that, update that so we can talk extra then.
**[00:00:45] Aaman A:** But for now, main things I wanted to address is two things, actually, which is the first thing I wanted to mention is, I was looking at the, obviously, I want to hear what you've been doing, or, like, what you think of it.
**[00:00:58] Aaman A:** But I think...
**[00:00:59] Aaman A:** What we should do, by the end of this week, let us automate, or at least get 90% of the entire email and SMS copy creation.
**[00:01:11] Aaman A:** Not the strategy and stuff like that, the copy creation.
**[00:01:15] Aaman A:** So what good looks like is, maybe I can, because I think the strategy is so nuanced, as in there's so many decision trees when it comes to a GTM strategy.
**[00:01:27] Aaman A:** Rather, let me just do it.
**[00:01:29] Aaman A:** We have a lot of underperforming clients, right?
**[00:01:31] Aaman A:** So I'm going to jump in this week.
**[00:01:33] Aaman A:** So what I can do, and I just want to hear from you what I should do, I was thinking of documenting or recording a Loom as I was kind of doing the GTM strategy and what I want.
**[00:01:42] Aaman A:** The biggest time-consuming part is just the copy creation.
**[00:01:45] Aaman A:** But yeah, I just wanted to hear what you think.
**[00:01:48] Aaman A:** That's the first thing I wanted to mention.
**[00:01:50] Aaman A:** Okay.
**[00:01:52] Hilal Aziz:** So Aman, for copy creation, the system needs everything, like the whole ICP and all of the things.
**[00:02:00] Hilal Aziz:** Okay, so what I planned is just a fast way, like a fast speed run from which you go from the ICP till the copies.
**[00:02:11] Hilal Aziz:** Then I can create another skill, like you can use the same skill, you can just say to AI that this is my whole strategy.
**[00:02:19] Hilal Aziz:** I've shared the prompt for copy creation, you just have to paste that and AI will make the copy for you, okay, based on all the guidelines, SOPs, and rules to consider in the mine, and how winning SMS looks like.
**[00:02:32] Hilal Aziz:** So it will consider all these three to four elements, view your GTM strategy, and it will output the, what, say, a copy, okay.
**[00:02:43] Hilal Aziz:** So the purpose of this playbook is that it has all the skills that a GTM strategist performs, okay, because he can, like, pick up any skill and give the prerequisites to AI and say that now perform.
**[00:03:00] Hilal Aziz:** It's a skill and give me the answer, okay?
**[00:03:02] Hilal Aziz:** And, like, you are searching for the value props.
**[00:03:05] Hilal Aziz:** Now, there are multiple steps before value prop.
**[00:03:08] Hilal Aziz:** If you have them already, you can just use the scale of value proposition, and you can tell AI that consider this as the context and perform the job, and it will do it.
**[00:03:20] Hilal Aziz:** So all the skills are there.
**[00:03:21] Hilal Aziz:** And one more thing, it also has tools.
**[00:03:24] Hilal Aziz:** Like, if you want to, like, if you are on bad marketing, you are designing something for them.
**[00:03:30] Hilal Aziz:** You can just say, hey, Claude, go to my Fathom and check this email address.
**[00:03:35] Hilal Aziz:** You can provide the bad marketing email, and it will gather all the transcripts and save it in the folder as well so that it can refer to those transcripts.
**[00:03:44] Hilal Aziz:** Okay?
**[00:03:44] Hilal Aziz:** So that tool is also there.
**[00:03:46] Hilal Aziz:** Also, I am making another tool for Slack.
**[00:03:49] Hilal Aziz:** It will gather all the conversations from the channel of bad marketing.
**[00:03:53] Hilal Aziz:** So this way, AI has the full context about everything going through.
**[00:03:57] Hilal Aziz:** Then you can use those skills.
**[00:04:00] Hilal Aziz:** Growth-dosser skills, okay?
**[00:04:01] Hilal Aziz:** Cool.
**[00:04:02] Aaman A:** What I was thinking is, yeah, you're actually spot on, what I was thinking we should do is we should make a, I don't know what it's called, but like one subfold or sector that gives all the onboarding doc, the call transcripts, ICP, and stuff like that first, and then from there we can add sub-agents or sub-skills within that, that way we don't have to repeat the ICP every single time.
**[00:04:24] Aaman A:** But anyway, what I was thinking is we could make separate agents or separate skills for each one, which is like your copyright, even each and every copyright, so email, copywriter, separate skill, SMS, ICP, and then even a researcher as well.
**[00:04:41] Aaman A:** But what I'm thinking, yeah, how we can kind of isolate each and every part so that it doesn't  up.
**[00:04:47] Hilal Aziz:** Okay, so I have already did that.
**[00:04:50] Hilal Aziz:** Okay.
**[00:04:50] Hilal Aziz:** All the skills, all the SOPs are different, and every file has its own purpose, okay?
**[00:04:58] Hilal Aziz:** Like SMS copy.
**[00:05:00] Hilal Aziz:** running SMS, SMS rules are connected.
**[00:05:03] Hilal Aziz:** Same way the email copy, email guidelines are connected.
**[00:05:07] Hilal Aziz:** So this way, everything is connected within the loop behind the scenes.
**[00:05:11] Hilal Aziz:** Okay.
**[00:05:11] Hilal Aziz:** And the feedback that you just gave me that Fathom, find out these issues that this SMS requires a human touch, something like that.
**[00:05:20] Hilal Aziz:** I added that thing as a skill as well in the same SMS rules.
**[00:05:24] Hilal Aziz:** So AI tried to make a better copy.
**[00:05:28] Hilal Aziz:** Second one was lengthy, but I reiterated it and it became short.
**[00:05:33] Hilal Aziz:** So the second thing is that I have designed it like output folders.
**[00:05:40] Hilal Aziz:** In output, you will make a folder for the client, like digital resource.
**[00:05:44] Hilal Aziz:** Okay.
**[00:05:44] Hilal Aziz:** And in digital resource, AI will automatically make five folders, transcripts, Slack conversation, Fathom meeting, onboarding sheet that they fill with the persona and everything.
**[00:05:56] Hilal Aziz:** And the fifth one is the onboarding form question answered.
**[00:06:00] Hilal Aziz:** So these five folders are the context about the client, and then it will make another folder named as Client's Output by AI, something like that.
**[00:06:08] Hilal Aziz:** And in that folder, AI will put all the data AI makes regarding that client.
**[00:06:15] Hilal Aziz:** And you don't even have to share this with Khizar or Fahad.
**[00:06:20] Hilal Aziz:** Whenever they want to use the agent, they can use GitPull from GitHub, and it will take the latest structure of that repository from GitHub.
**[00:06:28] Hilal Aziz:** So if you are making changes to any client's output folder, and you don't want to share them, you just have to tell them, take a GitPull.
**[00:06:36] Hilal Aziz:** And all the outputs by AI and every research that you did with the agent will come on their PCs as well.
**[00:06:43] Hilal Aziz:** Okay.
**[00:06:44] Hilal Aziz:** Okay.
**[00:06:46] Aaman A:** Okay, so, cool.
**[00:06:49] Aaman A:** I think what we can do then is if you could kind of walk me through it on our call properly to see.
**[00:06:55] Aaman A:** Let's just do it with kinship on the current one that we have.
**[00:06:57] Aaman A:** And also, so with the ClickUp...
**[00:07:00] Aaman A:** What did you assign me?
**[00:07:01] Aaman A:** Did you assign me all the prompts that we're using as well?
**[00:07:03] Hilal Aziz:** Yes, it is the six structured prompts for each step, but you know better when to use them.
**[00:07:11] Hilal Aziz:** But it will be best if we do a meeting at 7.30, I can do a quick walkthrough to you.
**[00:07:17] Hilal Aziz:** You will be using them because you already know you can do the QA with AI as well in the same prompt.
**[00:07:24] Hilal Aziz:** Okay.
**[00:07:25] Hilal Aziz:** And my second suggestion is that whenever you are trying to use a skill, use a new chat because the context window overloads and AI hallucinates.
**[00:07:35] Hilal Aziz:** So you have to open a new chat every time you are giving a prompt because output of each prompt is being saved in a file that you can refer to in a new message.
**[00:07:44] Hilal Aziz:** Okay.
**[00:07:46] Hilal Aziz:** So this way everything is cool and we can increase the skills, we can apply more tools like I have enabled the search tool as well of Gina because Gina is like very good searcher.
**[00:07:57] Hilal Aziz:** So if AI wants to do some research.
**[00:08:00] Hilal Aziz:** It can do its own search as well, but it can also use GINA AI to do some, like, customized searching, like, Reddit threads or, like, Facebook posts or something.
**[00:08:10] Hilal Aziz:** So it is doing that as well.
**[00:08:12] Hilal Aziz:** Sounds good.
**[00:08:14] Aaman A:** Cool.
**[00:08:14] Aaman A:** So what I'm thinking is, let's go through that, and then, yeah, we'll talk about it then.
**[00:08:21] Aaman A:** The thing is, yeah, I just want to ensure those skills are accurate in terms of, as I already told you, the offer and value props to be outdated.
**[00:08:31] Aaman A:** Some of the things are a little bit outdated.
**[00:08:33] Aaman A:** I just want to see what's going on, and I can try and update it as well.
**[00:08:37] Aaman A:** And no problem with that.
**[00:08:38] Hilal Aziz:** Even, Aaman, you can just do the voice prompting, and it will change the skills.
**[00:08:42] Hilal Aziz:** So, like, it's totally a playbook.
**[00:08:45] Hilal Aziz:** You can just play with it and improve it by the time pass.
**[00:08:48] Aaman A:** Yeah, and I think we should focus on one client as well this week, or, like, so we can actually measure, okay, what...
**[00:08:54] Aaman A:** Yes.
**[00:08:55] Aaman A:** Yeah, do you know?
**[00:08:55] Aaman A:** All right, but we'll talk about it.
**[00:08:56] Aaman A:** We'll talk about it the other day.
**[00:08:58] Aaman A:** Okay, sure.
**[00:08:58] Aaman A:** Cool.
**[00:08:59] Aaman A:** Thanks a lot.
